"""ts_jev_cost_calculator.core — statistical token and cost estimator for TypeSafe (System One / Jev) requests.

Unofficial project, not affiliated with the service provider. The model was fitted on 2026-09-17 against the
`usage` counts returned by 1,364 requests sent by the author:
  input_tokens = base offset + T(serialize(state)) + Σ T(serialize(question_i)) + structural corrections
  T(text) = c0·proxy(text) + Σ c_i·feature_i(text)   [proxy mode, requires `tokenizers`]
          = Σ c_i·feature_i(text)                     [features mode, no dependencies]
The serialization is a modelling choice that fits the reported counts best; it implies no knowledge of how the
service works internally. Accuracy on 751 requests: proxy median 0.9%, p90 2.5%; features median 1.9%, p90 6.6%.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from typing import Any, Optional

PRICE_USD_PER_MTOK = 0.042          # public list price shown on docs.typesafe.ai as of 2026-09-17; override with price_usd_per_mtok
LIMIT_STATE_PLUS_LONGEST = 32_768   # threshold at which the tool warns; check the official documentation for current limits
LIMIT_TOTAL = 65_536                # threshold at which the tool warns; check the official documentation for current limits
RATE_REQ_PER_MIN = 1200             # as published in the public documentation at the time of writing; actual limits depend on the account
RATE_TOK_PER_SEC = 250_000          # idem

_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FEATURE_NAMES = ["chars", "words", "digits", "punct", "upper", "nonascii", "newlines", "longwords", "it_hint", "spaces_runs"]
STRUCT_NAMES = ["n_questions", "n_options", "n_levels", "n_noul_criteria", "state_structured"]
OUTPUT_NAMES = ["n_noul", "n_choice", "n_score", "n_opt", "n_lvl", "opt_key_tokens", "lvl_text_tokens"]
_IT_WORDS = {"di", "il", "la", "che", "per", "una", "non", "del", "della", "con", "sono", "gli", "le", "un", "è", "ho", "mi", "ma", "dei", "delle", "nel", "alla", "come", "anche"}

with open(os.path.join(_DATA, "cost_model.json"), encoding="utf-8") as _f:
    MODEL = json.load(_f)

_PROXY: Any = None


def _load_proxy():
    global _PROXY
    if _PROXY is None:
        try:
            from tokenizers import Tokenizer  # type: ignore
            _PROXY = Tokenizer.from_file(os.path.join(_DATA, "qwen2.5-tokenizer.json"))
        except Exception:
            _PROXY = False
    return _PROXY or None


def proxy_available() -> bool:
    """True when the `tokenizers` package is importable (precise mode)."""
    return _load_proxy() is not None


# ---------------------------------------------------------------- request serialization (modelling choice)
def render_state(state: Any) -> str:
    return state if isinstance(state, str) else json.dumps(state, ensure_ascii=False, indent=2)


def render_question(q: dict) -> str:
    t = q.get("type")
    body: dict = {}
    if q.get("instructions") is not None:
        body["instructions"] = q["instructions"]
    crit = q.get("criteria")
    if t == "score" and isinstance(crit, list):
        body["criteria"] = {str(i): v for i, v in enumerate(crit)}
    elif t == "choice" and isinstance(crit, dict):
        body["criteria"] = {k: ({"description": v} if v is not None else None) for k, v in crit.items()}
    elif t == "noul" and isinstance(crit, dict):
        kept = {k: v for k, v in crit.items() if k in ("true", "false")}
        if kept:
            body["criteria"] = kept
    elif crit is not None:
        body["criteria"] = crit
    for k, v in q.items():
        if k not in ("type", "instructions", "criteria"):
            body[k] = v
    return json.dumps(body, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- features and counting
def text_features(t: str) -> dict:
    words = re.findall(r"\S+", t)
    return {
        "chars": len(t), "words": len(words), "digits": sum(c.isdigit() for c in t),
        "punct": sum((not c.isalnum()) and (not c.isspace()) for c in t), "upper": sum(c.isupper() for c in t),
        "nonascii": sum(ord(c) > 127 for c in t), "newlines": t.count("\n"),
        "longwords": sum(1 for w in re.findall(r"[A-Za-z]+", t) if len(w) >= 12),
        "it_hint": sum(1 for w in re.findall(r"[a-zàèéìòù]+", t.lower()) if w in _IT_WORDS),
        "spaces_runs": len(re.findall(r" {2,}", t)),
    }


def _mode(use_proxy: bool) -> str:
    return "proxy" if (use_proxy and proxy_available() and "proxy" in MODEL["input"]) else "features"


def count_tokens(text: str, use_proxy: bool = True) -> float:
    """Estimated tokens of a piece of text as-is (without the per-request base offset)."""
    if not text:
        return 0.0
    mode = _mode(use_proxy)
    coef = MODEL["input"][mode]["coef"]
    f = text_features(text)
    row = ([len(_load_proxy().encode(text, add_special_tokens=False).ids)] if mode == "proxy" else []) + [f[k] for k in FEATURE_NAMES]
    return max(0.0, sum(a * b for a, b in zip(row, coef)))


def _struct_counts(doc: dict) -> dict:
    qs = doc.get("questions") or {}
    state = doc.get("state", doc.get("document"))
    return {
        "n_questions": len(qs),
        "n_options": sum(len(q.get("criteria") or {}) for q in qs.values() if q.get("type") == "choice"),
        "n_levels": sum(len(q.get("criteria") or []) for q in qs.values() if q.get("type") == "score"),
        "n_noul_criteria": sum(1 for q in qs.values() if q.get("type") == "noul" and isinstance(q.get("criteria"), dict) for k, v in q["criteria"].items() if k in ("true", "false") and v is not None),
        "state_structured": 0.0 if isinstance(state, str) or state is None else 1.0,
    }


@dataclass
class Estimate:
    """Result of `estimate()`. Token counts are estimates; `cost_usd` covers input tokens only (output is free)."""
    input_tokens: int
    output_tokens: int
    cost_usd: float
    mode: str                      # "proxy" or "features"
    base_tokens: int               # fitted per-request offset
    state_tokens: int
    question_tokens: int
    longest_question_tokens: int
    n_questions: int
    over_state_plus_longest_limit: bool
    over_total_limit: bool
    expected_error_median: Optional[float]
    expected_error_p90: Optional[float]

    @property
    def ok(self) -> bool:
        """False when the request exceeds one of the context thresholds."""
        return not (self.over_state_plus_longest_limit or self.over_total_limit)

    def cost_for(self, calls: int) -> float:
        return self.cost_usd * calls

    def max_calls_per_minute(self) -> int:
        return min(RATE_REQ_PER_MIN, int(RATE_TOK_PER_SEC * 60 / max(self.input_tokens, 1)))

    def to_dict(self) -> dict:
        d = asdict(self)
        d["ok"] = self.ok
        d["max_calls_per_minute"] = self.max_calls_per_minute()
        return d


def estimate(request: dict, use_proxy: bool = True, conservative: bool = False, price_usd_per_mtok: float = PRICE_USD_PER_MTOK) -> Estimate:
    """Estimate a request {state, model, questions} (or the bare `questions` map used by the Playground)."""
    doc = request if "questions" in request else {"state": "", "questions": request}
    mode = _mode(use_proxy)
    m = MODEL["input"][mode]
    state = doc.get("state", doc.get("document"))
    st_tok = count_tokens(render_state(state), use_proxy) if state is not None else 0.0
    q_tok = [count_tokens(render_question(q), use_proxy) for q in (doc.get("questions") or {}).values()]
    sc = _struct_counts(doc)
    struct = sum(sc[k] * v for k, v in zip(STRUCT_NAMES, m.get("struct_coef", [])))
    total = m["overhead"] + st_tok + sum(q_tok) + struct
    if conservative:
        total *= 1.0 + m.get("cv_p90_rel_err", 0.05)
    om = MODEL["output"]
    oc = {k: 0.0 for k in OUTPUT_NAMES}
    for q in (doc.get("questions") or {}).values():
        t = q.get("type")
        if t == "noul":
            oc["n_noul"] += 1
        elif t == "choice":
            oc["n_choice"] += 1
            for k in (q.get("criteria") or {}):
                oc["n_opt"] += 1
                oc["opt_key_tokens"] += count_tokens(k, use_proxy)
        elif t == "score":
            oc["n_score"] += 1
            for lv in (q.get("criteria") or []):
                oc["n_lvl"] += 1
                if lv is not None:
                    oc["lvl_text_tokens"] += count_tokens(lv if isinstance(lv, str) else json.dumps(lv, ensure_ascii=False), use_proxy)
    out = om["intercept"] + sum(oc[k] * om.get(k, 0.0) for k in OUTPUT_NAMES)
    longest = max(q_tok) if q_tok else 0.0
    return Estimate(
        input_tokens=int(round(total)), output_tokens=int(round(out)), cost_usd=total / 1e6 * price_usd_per_mtok, mode=mode,
        base_tokens=int(round(m["overhead"])), state_tokens=int(round(st_tok)), question_tokens=int(round(sum(q_tok))),
        longest_question_tokens=int(round(longest)), n_questions=len(doc.get("questions") or {}),
        over_state_plus_longest_limit=st_tok + longest > LIMIT_STATE_PLUS_LONGEST, over_total_limit=total > LIMIT_TOTAL,
        expected_error_median=m.get("cv_median_rel_err"), expected_error_p90=m.get("cv_p90_rel_err"),
    )


def actual_cost(response: dict, price_usd_per_mtok: float = PRICE_USD_PER_MTOK) -> dict:
    """Real cost of a completed request, read from the API response `usage` field.

    Accepts the raw API response, or a record that wraps it under a `response` key."""
    if "usage" not in response and isinstance(response.get("response"), dict):
        response = response["response"]
    u = response.get("usage") or {}
    inp = u.get("input_tokens") or 0
    return {"model": response.get("model"), "input_tokens": inp, "output_tokens": u.get("output_tokens") or 0, "cost_usd": inp / 1e6 * price_usd_per_mtok}

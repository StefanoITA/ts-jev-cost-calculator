"""General offline tests: no API key, no network. Run with `pytest` (or `python -m pytest`)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ts_jev_cost_calculator import (LIMIT_STATE_PLUS_LONGEST, PRICE_USD_PER_MTOK, Estimate, actual_cost, count_tokens, estimate, proxy_available)

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
REQUEST = json.loads((EXAMPLES / "request.json").read_text(encoding="utf-8"))
RESPONSE = json.loads((EXAMPLES / "response.json").read_text(encoding="utf-8"))
REAL_INPUT = RESPONSE["usage"]["input_tokens"]


def test_estimate_returns_dataclass_with_sane_values():
    e = estimate(REQUEST)
    assert isinstance(e, Estimate)
    assert e.n_questions == 3
    assert e.base_tokens > 0 and e.state_tokens > 0 and e.question_tokens > 0
    # the total also includes small fitted structural corrections, so the parts sum only approximately
    assert e.input_tokens == pytest.approx(e.base_tokens + e.state_tokens + e.question_tokens, rel=0.05)
    assert e.output_tokens > 0
    assert e.cost_usd == pytest.approx(e.input_tokens / 1e6 * PRICE_USD_PER_MTOK, rel=1e-3)
    assert e.ok
    assert e.mode in ("proxy", "features")


def test_estimate_is_close_to_the_recorded_real_usage():
    e = estimate(REQUEST)
    tolerance = 0.06 if e.mode == "proxy" else 0.15
    assert abs(e.input_tokens - REAL_INPUT) / REAL_INPUT < tolerance
    assert abs(e.output_tokens - RESPONSE["usage"]["output_tokens"]) / RESPONSE["usage"]["output_tokens"] < 0.25


def test_features_mode_works_without_the_proxy_tokenizer():
    e = estimate(REQUEST, use_proxy=False)
    assert e.mode == "features"
    assert abs(e.input_tokens - REAL_INPUT) / REAL_INPUT < 0.15


def test_bare_questions_map_is_accepted():
    e = estimate(REQUEST["questions"])
    assert e.n_questions == 3 and e.state_tokens == 0 and e.input_tokens > 0


def test_conservative_adds_a_margin_and_price_override_scales_cost():
    base = estimate(REQUEST)
    assert estimate(REQUEST, conservative=True).input_tokens > base.input_tokens
    assert estimate(REQUEST, price_usd_per_mtok=2 * PRICE_USD_PER_MTOK).cost_usd == pytest.approx(2 * base.cost_usd)
    assert base.cost_for(1000) == pytest.approx(1000 * base.cost_usd)


def test_context_limit_is_detected():
    big = dict(REQUEST, state="word " * 40_000)
    e = estimate(big)
    assert e.state_tokens + e.longest_question_tokens > LIMIT_STATE_PLUS_LONGEST
    assert e.over_state_plus_longest_limit and not e.ok


def test_count_tokens_grows_with_text_and_is_zero_for_empty():
    assert count_tokens("") == 0
    short, long = count_tokens("Hello world"), count_tokens("Hello world " * 50)
    assert 0 < short < long


def test_actual_cost_reads_usage_from_response_and_from_wrapped_record():
    r = actual_cost(RESPONSE)
    assert r["input_tokens"] == REAL_INPUT and r["model"] == RESPONSE["model"]
    assert r["cost_usd"] == pytest.approx(REAL_INPUT / 1e6 * PRICE_USD_PER_MTOK)
    assert actual_cost({"request": REQUEST, "response": RESPONSE})["input_tokens"] == REAL_INPUT


def test_to_dict_is_json_serializable():
    d = estimate(REQUEST).to_dict()
    json.dumps(d)
    assert d["ok"] is True and "max_calls_per_minute" in d


def _cli(*args, stdin=None):
    return subprocess.run([sys.executable, "-m", "ts_jev_cost_calculator.cli", *args], input=stdin, capture_output=True, text=True)


def test_cli_estimate_quiet_and_json():
    q = _cli("estimate", str(EXAMPLES / "request.json"), "-q")
    assert q.returncode == 0
    inp, out, cost = q.stdout.split()
    assert int(inp) > 0 and int(out) > 0 and float(cost) > 0
    j = _cli("estimate", str(EXAMPLES / "request.json"), "--json", "--calls", "10")
    d = json.loads(j.stdout)
    assert d["input_tokens"] == int(inp) and d["calls"] == 10 and d["cost_usd_total"] == pytest.approx(10 * float(cost), rel=1e-4)


def test_cli_reads_stdin_and_reports_usage_and_info():
    s = _cli("estimate", "-", "-q", stdin=json.dumps(REQUEST))
    assert s.returncode == 0 and len(s.stdout.split()) == 3
    u = _cli("usage", str(EXAMPLES / "response.json"))
    assert f"input_tokens={REAL_INPUT}" in u.stdout
    assert "price:" in _cli("info").stdout
    assert int(_cli("text", "Hello, world!").stdout) > 0


def test_cli_exit_codes_for_over_limit_and_invalid_json(tmp_path):
    big = tmp_path / "big.json"
    big.write_text(json.dumps(dict(REQUEST, state="word " * 40_000)), encoding="utf-8")
    assert _cli("estimate", str(big), "-q").returncode == 2
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    r = _cli("estimate", str(bad))
    assert r.returncode == 1 and "invalid JSON" in r.stderr


def test_quickstart_example_runs():
    r = subprocess.run([sys.executable, str(EXAMPLES / "quickstart.py")], capture_output=True, text=True)
    assert r.returncode == 0 and "real cost per call" in r.stdout


def test_proxy_flag_matches_installation():
    assert isinstance(proxy_available(), bool)

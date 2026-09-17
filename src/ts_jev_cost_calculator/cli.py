"""ts-jev-cost-calculator — command line (also installed as the short alias `tscost`).

  ts-jev-cost-calculator estimate request.json            estimated input/output tokens, cost, limits
  ts-jev-cost-calculator estimate - < request.json        from stdin
  ts-jev-cost-calculator estimate request.json --calls 100000 --json
  ts-jev-cost-calculator text "any text"                  estimated tokens of a text (or - for stdin)
  ts-jev-cost-calculator usage response.json              actual cost from the `usage` field of an API response
  ts-jev-cost-calculator info                             active mode, price, limits
  tscost estimate request.json                            same tool, short alias
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from . import __version__
from .core import LIMIT_STATE_PLUS_LONGEST, LIMIT_TOTAL, PRICE_USD_PER_MTOK, actual_cost, count_tokens, estimate, proxy_available


def _read_json(path: str) -> dict:
    data = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        sys.exit(f"invalid JSON ({e.msg} at line {e.lineno}, column {e.colno})")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]) if sys.argv and sys.argv[0] else "ts-jev-cost-calculator", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"ts-jev-cost-calculator {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("estimate", help="estimate a request (JSON file, or - for stdin)")
    e.add_argument("file")
    e.add_argument("--calls", type=int, default=1, help="project the cost over N calls")
    e.add_argument("--price", type=float, default=PRICE_USD_PER_MTOK, help="USD per million input tokens")
    e.add_argument("--conservative", action="store_true", help="add the 90th-percentile error as a safety margin")
    e.add_argument("--no-proxy", action="store_true", help="force the dependency-free mode")
    e.add_argument("--json", action="store_true", help="JSON output")
    e.add_argument("--quiet", "-q", action="store_true", help="print only: input_tokens output_tokens cost_usd")
    t = sub.add_parser("text", help="estimated tokens of a text")
    t.add_argument("text", help="text, or - for stdin")
    t.add_argument("--no-proxy", action="store_true")
    u = sub.add_parser("usage", help="actual cost from an API response")
    u.add_argument("file")
    u.add_argument("--price", type=float, default=PRICE_USD_PER_MTOK)
    sub.add_parser("info", help="mode, price, limits")
    a = ap.parse_args(argv)

    if a.cmd == "estimate":
        est = estimate(_read_json(a.file), use_proxy=not a.no_proxy, conservative=a.conservative, price_usd_per_mtok=a.price)
        if a.json:
            d = est.to_dict(); d["calls"] = a.calls; d["cost_usd_total"] = est.cost_for(a.calls)
            print(json.dumps(d, ensure_ascii=False, indent=2)); return
        if a.quiet:
            print(f"{est.input_tokens} {est.output_tokens} {est.cost_usd:.8f}"); sys.exit(0 if est.ok else 2)
        print(f"input_tokens   ~ {est.input_tokens:>8}   (base {est.base_tokens} + state {est.state_tokens} + {est.n_questions} questions {est.question_tokens})")
        print(f"output_tokens  ~ {est.output_tokens:>8}   (free)")
        print(f"cost           ~ ${est.cost_usd:.7f} per call" + (f"   -> ${est.cost_for(a.calls):.4f} for {a.calls} calls" if a.calls > 1 else ""))
        print(f"mode           {est.mode}" + (f"   (expected error: median {est.expected_error_median:.1%}, p90 {est.expected_error_p90:.1%})" if est.expected_error_median is not None else ""))
        print(f"rate limit     up to {est.max_calls_per_minute()} calls/min (documented limits; your account may differ)")
        if est.over_state_plus_longest_limit:
            print(f"WARNING        state + longest question ({est.state_tokens + est.longest_question_tokens}) exceeds the {LIMIT_STATE_PLUS_LONGEST} threshold: the request will likely be rejected")
        if est.over_total_limit:
            print(f"WARNING        total ({est.input_tokens}) exceeds the {LIMIT_TOTAL} threshold: the request will likely be rejected")
        sys.exit(0 if est.ok else 2)
    elif a.cmd == "text":
        txt = sys.stdin.read() if a.text == "-" else a.text
        print(round(count_tokens(txt, use_proxy=not a.no_proxy)))
    elif a.cmd == "usage":
        r = actual_cost(_read_json(a.file), price_usd_per_mtok=a.price)
        print(f"model={r['model']} input_tokens={r['input_tokens']} output_tokens={r['output_tokens']} cost_usd={r['cost_usd']:.8f}")
    else:
        print(f"ts-jev-cost-calculator {__version__}")
        print(f"mode: {'proxy (tokenizers available, precise)' if proxy_available() else 'features (the tokenizers package is missing: run `pip install tokenizers` for the precise mode)'}")
        print("commands: ts-jev-cost-calculator, tscost (alias)")
        print(f"price: ${PRICE_USD_PER_MTOK} per million input tokens; output tokens are free")
        print(f"limits: {LIMIT_STATE_PLUS_LONGEST} tokens for state + longest question, {LIMIT_TOTAL} total")


if __name__ == "__main__":
    main()

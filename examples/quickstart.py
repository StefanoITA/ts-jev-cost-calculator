"""Quickstart: estimate a request before sending it, then read the real cost from the response.

Run from the repository root after installing the package:
    python examples/quickstart.py
No API key or network access is needed: the response used here is a recorded one.
"""
import json
from pathlib import Path

from ts_jev_cost_calculator import actual_cost, count_tokens, estimate

HERE = Path(__file__).parent
request = json.loads((HERE / "request.json").read_text(encoding="utf-8"))
response = json.loads((HERE / "response.json").read_text(encoding="utf-8"))

# 1. Before sending: estimate tokens, cost and limits.
e = estimate(request)
print(f"estimated input tokens : {e.input_tokens}")
print(f"estimated output tokens: {e.output_tokens}")
print(f"estimated cost per call: ${e.cost_usd:.7f}")
print(f"cost for 100,000 calls : ${e.cost_for(100_000):.2f}")
print(f"within context limits  : {e.ok}")
print(f"mode                   : {e.mode}")

# 2. After sending: the real cost comes from the response, nothing is estimated.
real = actual_cost(response)
print(f"real input tokens      : {real['input_tokens']}  (model {real['model']})")
print(f"real cost per call     : ${real['cost_usd']:.7f}")
print(f"estimate error         : {abs(e.input_tokens - real['input_tokens']) / real['input_tokens']:.2%}")

# 3. Tokens of an arbitrary piece of text.
print(f"tokens of the state    : {count_tokens(request['state']):.0f}")

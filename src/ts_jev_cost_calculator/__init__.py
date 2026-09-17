"""ts-jev-cost-calculator — estimate tokens and cost of a TypeSafe (Jev) request before sending it.

Unofficial, independent project: not affiliated with or endorsed by TypeSafe. All figures are estimates.

    from ts_jev_cost_calculator import estimate
    e = estimate({"state": "...", "model": "jev-latest", "questions": {...}})
    e.input_tokens, e.output_tokens, e.cost_usd, e.ok
"""
from .core import (LIMIT_STATE_PLUS_LONGEST, LIMIT_TOTAL, PRICE_USD_PER_MTOK, Estimate, actual_cost, count_tokens, estimate, proxy_available)

__all__ = ["estimate", "count_tokens", "actual_cost", "Estimate", "proxy_available", "PRICE_USD_PER_MTOK", "LIMIT_STATE_PLUS_LONGEST", "LIMIT_TOTAL"]
__version__ = "1.0.0"

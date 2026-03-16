from __future__ import annotations

from typing import Any

from value_check.app.models import ValuationSnapshot
from value_check.app.utils.math_utils import safe_divide


def calculate_current_metrics(snapshot: ValuationSnapshot, treasury_yield: float) -> tuple[dict[str, Any], list[str]]:
    caveats: list[str] = []

    pe_ratio = safe_divide(snapshot.market_cap, snapshot.net_income_ttm)
    if snapshot.net_income_ttm is not None and snapshot.net_income_ttm <= 0:
        caveats.append("P/E is not meaningful because trailing earnings are negative.")
        pe_ratio = None

    ev_ebitda = safe_divide(snapshot.enterprise_value, snapshot.ebitda_ttm)
    if snapshot.asset_type == "stock" and snapshot.sector == "Financials":
        caveats.append("EV/EBITDA is less informative for financial companies.")
    if snapshot.ebitda_ttm is not None and snapshot.ebitda_ttm <= 0:
        caveats.append("EV/EBITDA is not meaningful because EBITDA is negative.")
        ev_ebitda = None

    ps_ratio = safe_divide(snapshot.market_cap, snapshot.revenue_ttm)
    pb_ratio = safe_divide(snapshot.market_cap, snapshot.book_value)
    if snapshot.book_value is not None and snapshot.book_value <= 0:
        caveats.append("P/B is not meaningful because book value is negative or near zero.")
        pb_ratio = None

    fcf_yield = safe_divide(snapshot.free_cash_flow_ttm, snapshot.market_cap)
    if snapshot.free_cash_flow_ttm is not None and snapshot.free_cash_flow_ttm <= 0:
        caveats.append("Free cash flow yield is negative, so valuation signals are less stable than usual.")
    earnings_yield = safe_divide(snapshot.net_income_ttm, snapshot.market_cap)
    treasury_relative_fcf_spread = None if fcf_yield is None else fcf_yield - treasury_yield

    if snapshot.asset_type == "etf":
        caveats.append("ETF valuation metrics are proxy-based and may be less consistent than single-stock fundamentals.")
        if snapshot.valuation_proxy_note:
            caveats.append(snapshot.valuation_proxy_note)

    metrics = {
        "pe_ratio": pe_ratio,
        "ev_ebitda": ev_ebitda,
        "ps_ratio": ps_ratio,
        "pb_ratio": pb_ratio,
        "fcf_yield": fcf_yield,
        "earnings_yield": earnings_yield,
        "treasury_relative_fcf_spread": treasury_relative_fcf_spread,
        "treasury_yield": treasury_yield,
    }
    return metrics, caveats

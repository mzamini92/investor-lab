from __future__ import annotations

from earnings_clarity.app.models import HoldingPosition
from earnings_clarity.app.services.analyzer import EarningsClarityAnalyzer


def analyze_portfolio_quarter(
    analyzer: EarningsClarityAnalyzer,
    holdings: list[HoldingPosition],
    quarter: str,
) -> list[dict[str, object]]:
    results = []
    for holding in holdings:
        prior_quarter = _infer_prior_quarter(quarter)
        analysis = analyzer.analyze_saved_call(holding.ticker, quarter, prior_quarter=prior_quarter)
        payload = analysis.to_dict()
        payload["shares_owned"] = holding.shares
        results.append(payload)
    return results


def _infer_prior_quarter(quarter: str) -> str | None:
    if len(quarter) != 6 or "Q" not in quarter:
        return None
    year = int(quarter[:4])
    q = int(quarter[-1])
    if q > 1:
        return f"{year}Q{q - 1}"
    return f"{year - 1}Q4"

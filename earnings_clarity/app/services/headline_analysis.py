from __future__ import annotations

from earnings_clarity.app.models import EarningsEvent


def _pct_diff(actual: float, estimate: float) -> float:
    return 0.0 if estimate == 0 else ((actual - estimate) / abs(estimate)) * 100.0


def _classification(diff_pct: float) -> str:
    if diff_pct > 2.0:
        return "beat"
    if diff_pct < -2.0:
        return "miss"
    return "inline"


def analyze_headline_result(event: EarningsEvent) -> dict[str, float | str]:
    revenue_surprise_pct = _pct_diff(event.revenue_actual, event.revenue_estimate)
    eps_surprise_pct = _pct_diff(event.eps_actual, event.eps_estimate)
    revenue_classification = _classification(revenue_surprise_pct)
    eps_classification = _classification(eps_surprise_pct)
    composite = (revenue_surprise_pct * 0.45) + (eps_surprise_pct * 0.55)
    headline_label = _classification(composite)
    return {
        "revenue_surprise_pct": round(revenue_surprise_pct, 2),
        "eps_surprise_pct": round(eps_surprise_pct, 2),
        "revenue_classification": revenue_classification,
        "eps_classification": eps_classification,
        "headline_classification": headline_label,
        "composite_surprise_score": round(composite, 2),
    }

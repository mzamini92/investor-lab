from earnings_clarity.app.models import EarningsEvent
from earnings_clarity.app.services.headline_analysis import analyze_headline_result


def test_headline_analysis_computes_surprise_and_classification() -> None:
    event = EarningsEvent(
        ticker="AAPL",
        company_name="Apple",
        quarter="2025Q4",
        earnings_date="2025-10-30",
        revenue_actual=102.0,
        revenue_estimate=100.0,
        eps_actual=2.10,
        eps_estimate=2.00,
    )
    result = analyze_headline_result(event)
    assert result["revenue_surprise_pct"] == 2.0
    assert result["eps_surprise_pct"] == 5.0
    assert result["headline_classification"] == "beat"

from economic_regime_translator.app.models import MacroSnapshot
from economic_regime_translator.app.services.analyzer import EconomicRegimeAnalyzer


def test_regime_label_soft_landing() -> None:
    analyzer = EconomicRegimeAnalyzer()
    snapshot = MacroSnapshot(
        observation_date="2026-02-28",
        fed_funds_rate=5.25,
        fed_funds_3m_change=-0.25,
        cpi_yoy=2.8,
        core_cpi_yoy=3.0,
        inflation_3m_annualized=2.4,
        unemployment_rate=4.2,
        unemployment_3m_change=0.2,
        ism_manufacturing=50.8,
        ism_services=52.3,
        real_policy_rate=2.85,
        yield_2y=4.15,
        yield_10y=4.05,
        term_spread_2s10s=-0.10,
        high_yield_spread=3.9,
        investment_grade_spread=1.25,
        earnings_revision_breadth=0.08,
        earnings_revision_momentum=0.03,
    )
    result = analyzer.classify(snapshot)
    assert result.regime_label == "Disinflationary soft landing"
    assert result.confidence_score >= 55

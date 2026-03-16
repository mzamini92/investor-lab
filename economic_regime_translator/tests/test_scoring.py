from economic_regime_translator.app.models import MacroSnapshot
from economic_regime_translator.app.services.normalization import normalize_snapshot
from economic_regime_translator.app.services.scoring import build_scorecard


def test_credit_stress_and_curve_warning_scores() -> None:
    snapshot = MacroSnapshot(
        observation_date="2026-01-31",
        fed_funds_rate=5.5,
        fed_funds_3m_change=0.0,
        cpi_yoy=3.2,
        core_cpi_yoy=3.4,
        inflation_3m_annualized=3.0,
        unemployment_rate=4.1,
        unemployment_3m_change=0.3,
        ism_manufacturing=48.0,
        yield_2y=4.6,
        yield_10y=3.8,
        term_spread_2s10s=-0.8,
        high_yield_spread=5.8,
        investment_grade_spread=1.9,
        earnings_revision_breadth=-0.2,
        earnings_revision_momentum=-0.08,
    )
    scorecard = build_scorecard(snapshot, normalize_snapshot(snapshot))
    assert scorecard["credit_stress_score"] > 60
    assert scorecard["curve_warning_score"] > 60
    assert scorecard["recession_risk_score"] > 60

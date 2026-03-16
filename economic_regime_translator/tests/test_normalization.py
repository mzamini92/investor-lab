from economic_regime_translator.app.models import MacroSnapshot
from economic_regime_translator.app.services.normalization import normalize_snapshot


def test_normalization_states() -> None:
    snapshot = MacroSnapshot(
        observation_date="2026-01-31",
        fed_funds_rate=5.25,
        fed_funds_3m_change=-0.25,
        cpi_yoy=2.8,
        core_cpi_yoy=3.0,
        inflation_3m_annualized=2.2,
        unemployment_rate=4.2,
        unemployment_3m_change=0.25,
        ism_manufacturing=50.5,
        yield_2y=4.2,
        yield_10y=4.0,
        term_spread_2s10s=-0.2,
        high_yield_spread=4.1,
        earnings_revision_breadth=0.05,
        earnings_revision_momentum=0.02,
    )
    states = normalize_snapshot(snapshot)
    assert states["inflation_trend"] == "cooling"
    assert states["curve_state"] == "inverted"
    assert states["credit_state"] == "caution"

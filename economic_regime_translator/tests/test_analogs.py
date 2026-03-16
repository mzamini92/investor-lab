import pandas as pd

from economic_regime_translator.app.models import MacroSnapshot
from economic_regime_translator.app.services.analogs import find_historical_analogs


def test_historical_analogs_return_matches() -> None:
    history = pd.DataFrame(
        [
            {
                "observation_date": "2016-08-31",
                "fed_funds_rate": 0.5,
                "cpi_yoy": 1.1,
                "inflation_3m_annualized": 1.4,
                "unemployment_rate": 4.9,
                "unemployment_3m_change": -0.1,
                "ism_manufacturing": 52.8,
                "term_spread_2s10s": 0.8,
                "high_yield_spread": 4.8,
                "earnings_revision_breadth": 0.10,
                "regime_label": "Disinflationary soft landing",
                "summary": "Soft landing analog",
                "us_equities_3m": 0.06,
            },
            {
                "observation_date": "2008-10-31",
                "fed_funds_rate": 1.0,
                "cpi_yoy": 3.7,
                "inflation_3m_annualized": 1.5,
                "unemployment_rate": 6.6,
                "unemployment_3m_change": 1.2,
                "ism_manufacturing": 38.9,
                "term_spread_2s10s": 2.0,
                "high_yield_spread": 8.5,
                "earnings_revision_breadth": -0.28,
                "regime_label": "Credit stress regime",
                "summary": "Stress analog",
                "us_equities_3m": -0.22,
            },
        ]
    )
    snapshot = MacroSnapshot(
        observation_date="2026-02-28",
        fed_funds_rate=0.6,
        fed_funds_3m_change=0.0,
        cpi_yoy=1.2,
        core_cpi_yoy=1.8,
        inflation_3m_annualized=1.3,
        unemployment_rate=4.8,
        unemployment_3m_change=-0.1,
        ism_manufacturing=53.0,
        yield_2y=0.8,
        yield_10y=1.6,
        term_spread_2s10s=0.8,
        high_yield_spread=4.7,
        earnings_revision_breadth=0.11,
    )
    analogs = find_historical_analogs(snapshot, history, top_n=1)
    assert analogs[0]["regime_label"] == "Disinflationary soft landing"

from __future__ import annotations

from economic_regime_translator.app.models import MacroSnapshot


REQUIRED_FIELDS = [
    "fed_funds_rate",
    "fed_funds_3m_change",
    "cpi_yoy",
    "core_cpi_yoy",
    "inflation_3m_annualized",
    "unemployment_rate",
    "unemployment_3m_change",
    "ism_manufacturing",
    "yield_2y",
    "yield_10y",
    "term_spread_2s10s",
    "high_yield_spread",
    "earnings_revision_breadth",
]


def validate_snapshot(snapshot: MacroSnapshot) -> None:
    for field_name in REQUIRED_FIELDS:
        if getattr(snapshot, field_name) is None:
            raise ValueError(f"Missing required snapshot field: {field_name}")

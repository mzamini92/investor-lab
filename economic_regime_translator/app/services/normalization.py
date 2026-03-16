from __future__ import annotations

from typing import Any

import pandas as pd

from economic_regime_translator.app.models import MacroSnapshot
from economic_regime_translator.app.utils.validation import validate_snapshot


def _inflation_trend(snapshot: MacroSnapshot) -> str:
    gap = snapshot.inflation_3m_annualized - snapshot.cpi_yoy
    if gap <= -0.3:
        return "cooling"
    if gap >= 0.4:
        return "reheating"
    return "sticky"


def _labor_trend(snapshot: MacroSnapshot) -> str:
    if snapshot.unemployment_3m_change >= 0.35:
        return "loosening"
    if snapshot.unemployment_3m_change <= -0.15:
        return "tightening"
    return "stable"


def _curve_state(snapshot: MacroSnapshot) -> str:
    spread = snapshot.term_spread_2s10s
    if spread <= -0.5:
        return "deeply_inverted"
    if spread < 0:
        return "inverted"
    if spread < 0.35:
        return "flat"
    if spread < 1.0:
        return "normal"
    return "steep"


def _credit_state(snapshot: MacroSnapshot) -> str:
    if snapshot.high_yield_spread >= 5.5:
        return "stressed"
    if snapshot.high_yield_spread >= 4.0:
        return "caution"
    return "benign"


def _earnings_state(snapshot: MacroSnapshot) -> str:
    momentum = snapshot.earnings_revision_momentum or 0.0
    if snapshot.earnings_revision_breadth >= 0.15 and momentum >= 0.05:
        return "improving"
    if snapshot.earnings_revision_breadth <= -0.15 or momentum <= -0.05:
        return "deteriorating"
    return "mixed"


def _growth_trend(snapshot: MacroSnapshot) -> str:
    if snapshot.ism_manufacturing >= 53 and snapshot.unemployment_3m_change <= 0.0:
        return "accelerating"
    if snapshot.ism_manufacturing < 49 or snapshot.unemployment_3m_change >= 0.25:
        return "slowing"
    return "steady"


def normalize_snapshot(snapshot: MacroSnapshot) -> dict[str, Any]:
    validate_snapshot(snapshot)
    real_rate = snapshot.real_policy_rate
    if real_rate is None:
        real_rate = snapshot.fed_funds_rate - snapshot.inflation_3m_annualized

    service_level = snapshot.ism_services if snapshot.ism_services is not None else snapshot.ism_manufacturing
    policy_direction = "easing" if snapshot.fed_funds_3m_change < -0.1 else "tightening" if snapshot.fed_funds_3m_change > 0.1 else "on_hold"

    return {
        "observation_date": snapshot.observation_date,
        "inflation_trend": _inflation_trend(snapshot),
        "labor_trend": _labor_trend(snapshot),
        "curve_state": _curve_state(snapshot),
        "credit_state": _credit_state(snapshot),
        "earnings_state": _earnings_state(snapshot),
        "growth_trend": _growth_trend(snapshot),
        "policy_direction": policy_direction,
        "policy_restrictiveness_proxy": real_rate,
        "manufacturing_signal": snapshot.ism_manufacturing,
        "services_signal": service_level,
        "earnings_momentum_proxy": snapshot.earnings_revision_momentum or snapshot.earnings_revision_breadth,
        "credit_proxy": snapshot.high_yield_spread,
        "curve_proxy": snapshot.term_spread_2s10s,
    }


def history_from_rows(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows)

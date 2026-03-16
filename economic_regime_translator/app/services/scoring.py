from __future__ import annotations

from typing import Any

from economic_regime_translator.app.models import MacroSnapshot
from economic_regime_translator.app.utils.math_utils import clamp, normalize_to_score


def build_scorecard(snapshot: MacroSnapshot, indicator_states: dict[str, Any]) -> dict[str, float]:
    growth_components = [
        normalize_to_score(snapshot.ism_manufacturing, 45.0, 58.0),
        normalize_to_score(-snapshot.unemployment_3m_change, -0.6, 0.4),
        normalize_to_score(snapshot.earnings_revision_breadth, -0.4, 0.4),
    ]
    inflation_components = [
        normalize_to_score(snapshot.cpi_yoy, 1.5, 5.5),
        normalize_to_score(snapshot.inflation_3m_annualized, 1.0, 5.5),
    ]
    policy_source = (
        snapshot.real_policy_rate
        if snapshot.real_policy_rate is not None
        else snapshot.fed_funds_rate - snapshot.inflation_3m_annualized
    )
    policy_components = [
        normalize_to_score(policy_source, -1.0, 3.0),
        normalize_to_score(snapshot.fed_funds_rate, 0.0, 6.0),
    ]
    credit_components = [
        normalize_to_score(snapshot.high_yield_spread, 2.5, 7.5),
        normalize_to_score(snapshot.investment_grade_spread or 1.2, 0.7, 2.5),
    ]
    earnings_components = [
        normalize_to_score(snapshot.earnings_revision_breadth, -0.4, 0.4),
        normalize_to_score(snapshot.earnings_revision_momentum or 0.0, -0.2, 0.2),
    ]

    curve_warning = 100.0 - normalize_to_score(snapshot.term_spread_2s10s, -1.0, 1.5)
    recession_risk = clamp(
        (
            0.25 * curve_warning
            + 0.20 * sum(credit_components) / len(credit_components)
            + 0.20 * normalize_to_score(snapshot.unemployment_3m_change, -0.2, 0.8)
            + 0.20 * (100.0 - sum(earnings_components) / len(earnings_components))
            + 0.15 * (100.0 - sum(growth_components) / len(growth_components))
        ),
        0.0,
        100.0,
    )
    risk_appetite = clamp(
        100.0
        - (
            0.35 * sum(credit_components) / len(credit_components)
            + 0.25 * curve_warning
            + 0.20 * normalize_to_score(snapshot.fed_funds_rate, 0.0, 6.0)
            + 0.20 * normalize_to_score(-(snapshot.equity_breadth or 0.0), -0.25, 0.25)
        ),
        0.0,
        100.0,
    )

    return {
        "growth_score": round(sum(growth_components) / len(growth_components), 2),
        "inflation_score": round(sum(inflation_components) / len(inflation_components), 2),
        "policy_restrictiveness_score": round(sum(policy_components) / len(policy_components), 2),
        "credit_stress_score": round(sum(credit_components) / len(credit_components), 2),
        "earnings_momentum_score": round(sum(earnings_components) / len(earnings_components), 2),
        "curve_warning_score": round(curve_warning, 2),
        "recession_risk_score": round(recession_risk, 2),
        "risk_appetite_score": round(risk_appetite, 2),
    }


def compute_confidence(scorecard: dict[str, float], regime_label: str) -> float:
    supportive = []
    conflicting = []

    if regime_label == "Disinflationary soft landing":
        supportive = [
            scorecard["growth_score"] >= 50,
            scorecard["inflation_score"] <= 55,
            scorecard["credit_stress_score"] <= 45,
            scorecard["earnings_momentum_score"] >= 45,
        ]
    elif regime_label in {"Credit stress regime", "Full recession contraction"}:
        supportive = [
            scorecard["credit_stress_score"] >= 60,
            scorecard["recession_risk_score"] >= 65,
            scorecard["growth_score"] <= 45,
        ]
    else:
        supportive = [
            scorecard["recession_risk_score"] >= 55 or scorecard["growth_score"] >= 55,
            scorecard["curve_warning_score"] >= 45 or scorecard["credit_stress_score"] <= 55,
        ]

    conflicting = [
        scorecard["growth_score"] > 70 and scorecard["recession_risk_score"] > 70,
        scorecard["inflation_score"] < 40 and scorecard["policy_restrictiveness_score"] < 30,
    ]
    raw = 55.0 + (sum(1 for item in supportive if item) * 10.0) - (sum(1 for item in conflicting if item) * 12.5)
    return round(clamp(raw, 25.0, 95.0), 2)

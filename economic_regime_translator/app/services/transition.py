from __future__ import annotations

from typing import Any


KEY_SCORE_FIELDS = [
    "growth_score",
    "inflation_score",
    "policy_restrictiveness_score",
    "credit_stress_score",
    "earnings_momentum_score",
    "curve_warning_score",
    "recession_risk_score",
]


def compare_regimes(current: dict[str, Any], prior: dict[str, Any]) -> dict[str, Any]:
    changed = []
    for key in KEY_SCORE_FIELDS:
        delta = float(current["scorecard"][key]) - float(prior["scorecard"][key])
        changed.append({"score": key, "delta": round(delta, 2)})
    changed = sorted(changed, key=lambda item: abs(item["delta"]), reverse=True)

    transition_label = "unchanged"
    if current["regime_label"] != prior["regime_label"]:
        transition_label = "regime_transition"
    elif current["scorecard"]["recession_risk_score"] - prior["scorecard"]["recession_risk_score"] >= 8:
        transition_label = "meaningful_deterioration"
    elif prior["scorecard"]["recession_risk_score"] - current["scorecard"]["recession_risk_score"] >= 8:
        transition_label = "meaningful_improvement"

    strongest_positive = max(changed, key=lambda item: item["delta"])
    strongest_negative = min(changed, key=lambda item: item["delta"])
    summary = (
        f"The regime moved from {prior['regime_label']} to {current['regime_label']}."
        if current["regime_label"] != prior["regime_label"]
        else f"The regime label stayed at {current['regime_label']}, but the underlying score mix shifted."
    )

    return {
        "transition_label": transition_label,
        "transition_summary": summary,
        "changed_indicators": changed[:5],
        "strongest_positive_shift": strongest_positive["score"],
        "strongest_negative_shift": strongest_negative["score"],
    }

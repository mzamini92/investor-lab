from __future__ import annotations

from typing import Any


def build_plain_english_summary(
    *,
    regime_label: str,
    confidence_score: float,
    indicator_states: dict[str, Any],
    scorecard: dict[str, float],
    classification: dict[str, Any],
    analogs: list[dict[str, Any]],
    portfolio_implications: dict[str, Any],
) -> dict[str, Any]:
    analog_note = ""
    if analogs:
        analog_note = (
            f"This looks most similar to {analogs[0]['observation_date']} "
            f"({analogs[0]['regime_label']})."
        )

    bullets = [
        f"Inflation trend: {indicator_states['inflation_trend']}.",
        f"Growth trend: {indicator_states['growth_trend']} with a growth score of {scorecard['growth_score']:.0f}/100.",
        f"Policy stance: {indicator_states['policy_direction']} with restrictiveness at {scorecard['policy_restrictiveness_score']:.0f}/100.",
        f"Credit conditions: {indicator_states['credit_state']} and a credit stress score of {scorecard['credit_stress_score']:.0f}/100.",
        f"Earnings revisions are {indicator_states['earnings_state']}, which matters for how durable risk appetite really is.",
    ]
    paragraph = (
        f"Current regime: {regime_label}. Confidence is {confidence_score:.0f}/100. "
        f"{classification['primary_drivers'][0]} {analog_note} {portfolio_implications['paragraph']}"
    ).strip()

    return {
        "one_line_label": regime_label,
        "summary_paragraph": paragraph,
        "five_bullet_explanation": bullets,
        "historical_precedent_note": analog_note,
        "portfolio_implication_note": portfolio_implications["paragraph"],
    }

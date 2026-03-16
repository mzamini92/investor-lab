from __future__ import annotations

from typing import Any


def build_alerts(
    *,
    moat_label: str,
    transition_label: str,
    signal_breakdown: list[dict[str, Any]],
    commentary_findings: dict[str, Any],
    streaks: dict[str, int],
) -> tuple[list[str], dict[str, Any]]:
    alerts: list[str] = []

    gross_margin_signal = next((row for row in signal_breakdown if row["signal_name"] == "gross_margin_trajectory"), None)
    roic_signal = next((row for row in signal_breakdown if row["signal_name"] == "roic_spread"), None)
    share_signal = next((row for row in signal_breakdown if row["signal_name"] == "market_share"), None)

    if moat_label in {"Orange", "Red"}:
        alerts.append(f"Moat health is now {moat_label}, which points to a clearer deterioration pattern than a typical noisy quarter.")
    if transition_label in {"early erosion", "clear deterioration"}:
        alerts.append(f"Moat trend has shifted to {transition_label.replace('_', ' ')} versus last quarter.")
    if streaks.get("gross_margin_compression", 0) >= 3:
        alerts.append(f"Gross margin has compressed for {streaks['gross_margin_compression']} consecutive quarters.")
    if streaks.get("roic_spread_narrowing", 0) >= 3:
        alerts.append(f"ROIC spread has narrowed for {streaks['roic_spread_narrowing']} consecutive quarters.")
    if commentary_findings["negative_signals"]:
        alerts.append(
            "Management commentary flagged pressure around "
            + ", ".join(commentary_findings["negative_signals"][:3])
            + "."
        )

    caution_level = "low"
    if moat_label in {"Orange", "Red"} or (
        gross_margin_signal and gross_margin_signal["current_status"] == "compressing" and roic_signal and roic_signal["current_status"] == "narrowing spread"
    ):
        caution_level = "high"
    elif moat_label == "Yellow" or (share_signal and share_signal["current_status"] == "losing share"):
        caution_level = "moderate"

    rationale_parts = []
    if gross_margin_signal:
        rationale_parts.append(gross_margin_signal["current_status"])
    if roic_signal:
        rationale_parts.append(roic_signal["current_status"])
    if share_signal:
        rationale_parts.append(share_signal["current_status"])

    caution = {
        "caution_level": caution_level,
        "rationale": "Pattern reflects " + ", ".join(rationale_parts[:3]) + "." if rationale_parts else "Pattern is mixed.",
        "watch_items": alerts[:3],
    }
    return alerts, caution

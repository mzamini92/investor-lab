from __future__ import annotations

from typing import Any


def build_interpretation(
    *,
    ticker: str,
    moat_label: str,
    moat_score: float,
    transition_label: str,
    signal_breakdown: list[dict[str, Any]],
    commentary_findings: dict[str, Any],
    peer_comparison: list[dict[str, Any]],
) -> tuple[str, str, list[str], dict[str, Any]]:
    strongest_positive = [row for row in signal_breakdown if row["strength_score"] >= 65]
    strongest_negative = [row for row in signal_breakdown if row["strength_score"] <= 40]
    watch_items: list[str] = []

    if strongest_negative:
        watch_items.append(f"Watch whether {strongest_negative[0]['signal_name'].replace('_', ' ')} keeps weakening next quarter.")
    if commentary_findings["negative_signals"]:
        watch_items.append("Monitor whether management keeps sounding more defensive on competition, pricing, or customer demand.")
    if any(row["peer_interpretation"] == "weaker than peers" for row in peer_comparison):
        watch_items.append("Peer comparison suggests relative edge may be narrowing in at least one moat dimension.")
    if strongest_positive:
        watch_items.append(f"Keep tracking whether {strongest_positive[0]['signal_name'].replace('_', ' ')} remains a source of resilience.")

    short_verdict = f"{ticker} moat health is {moat_label} ({moat_score:.1f}/100)."
    if transition_label == "strengthening":
        takeaway = f"{ticker} looks to be strengthening its competitive position versus last quarter, with enough quantitative support to treat this as more than narrative noise."
    elif transition_label in {"early erosion", "clear deterioration"}:
        takeaway = f"{ticker} does not necessarily have a broken thesis, but the moat looks less clearly intact than it did a few quarters ago."
    else:
        takeaway = f"{ticker} still looks broadly intact, though the signal mix is worth monitoring rather than assuming the moat is self-sustaining."

    bullets = [
        f"Moat health label: {moat_label}.",
        f"Transition vs last quarter: {transition_label.replace('_', ' ')}.",
        "The score combines margins, ROIC spread, pricing power, market share, reinvestment, sales efficiency, and commentary pressure.",
        "Moat changes are usually gradual, so repeated weak quarters matter more than a single noisy print.",
        "This is a thesis-monitoring tool, not a buy or sell recommendation.",
    ]
    return short_verdict, takeaway, watch_items[:4], {
        "one_line_verdict": short_verdict,
        "five_bullet_explanation": bullets,
        "long_term_holder_takeaway": takeaway,
    }

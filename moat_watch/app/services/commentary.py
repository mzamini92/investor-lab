from __future__ import annotations

from typing import Any

from moat_watch.app.models import CommentaryRecord
from moat_watch.app.utils.constants import COMMENTARY_KEYWORDS
from moat_watch.app.utils.math_utils import clamp


def analyze_commentary(record: CommentaryRecord | None) -> dict[str, Any]:
    if record is None:
        return {
            "positive_signals": [],
            "negative_signals": [],
            "pressure_score": 50.0,
            "supporting_snippets": [],
        }

    text = record.raw_commentary_text.lower()
    positive_signals: list[str] = []
    negative_signals: list[str] = []
    snippets: list[str] = []
    score = 50.0

    for label, phrases in COMMENTARY_KEYWORDS["negative"].items():
        if any(phrase in text for phrase in phrases):
            negative_signals.append(label.replace("_", " "))
            score -= 8.0
            snippets.append(f"Negative commentary flagged around {label.replace('_', ' ')}.")

    for label, phrases in COMMENTARY_KEYWORDS["positive"].items():
        if any(phrase in text for phrase in phrases):
            positive_signals.append(label.replace("_", " "))
            score += 7.0
            snippets.append(f"Positive commentary flagged around {label.replace('_', ' ')}.")

    if record.mentions_promotions or record.mentions_pricing_pressure:
        negative_signals.append("pricing pressure")
        score -= 8.0
    if record.mentions_competition:
        negative_signals.append("competition")
        score -= 6.0
    if record.mentions_customer_weakness:
        negative_signals.append("customer weakness")
        score -= 6.0
    if record.mentions_market_share_loss:
        negative_signals.append("market share loss")
        score -= 8.0
    if record.mentions_market_share_gain:
        positive_signals.append("market share gains")
        score += 8.0
    if record.mentions_innovation_strength:
        positive_signals.append("innovation strength")
        score += 7.0
    if record.mentions_cost_pressure:
        negative_signals.append("cost pressure")
        score -= 5.0

    return {
        "positive_signals": sorted(set(positive_signals)),
        "negative_signals": sorted(set(negative_signals)),
        "pressure_score": round(clamp(score, 0.0, 100.0), 2),
        "supporting_snippets": snippets[:5],
        "raw_commentary_text": record.raw_commentary_text,
    }

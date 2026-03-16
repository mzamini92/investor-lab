from __future__ import annotations

from value_check.app.utils.constants import VERDICT_BANDS


def map_score_to_verdict(score: float) -> str:
    for upper_bound, label in VERDICT_BANDS:
        if score < upper_bound:
            return label
    return "fair"


def build_verdict(score: float, reasons: list[str], confidence: float) -> dict[str, object]:
    return {
        "label": map_score_to_verdict(score),
        "score": round(score, 2),
        "confidence_score": round(confidence, 2),
        "reasoning_factors": reasons[:6],
    }

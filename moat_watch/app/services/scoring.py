from __future__ import annotations

from typing import Any

from moat_watch.app.models import SignalResult
from moat_watch.app.utils.constants import MOAT_LABEL_BANDS, MOAT_SCORE_WEIGHTS


def map_score_to_label(score: float) -> str:
    for threshold, label in MOAT_LABEL_BANDS:
        if score < threshold:
            return label
    return "Yellow"


def compute_moat_score(signals: list[SignalResult]) -> tuple[float, str, dict[str, float], float]:
    score_sum = 0.0
    weight_sum = 0.0
    component_scores: dict[str, float] = {}

    for signal in signals:
        weight = MOAT_SCORE_WEIGHTS.get(signal.signal_name, 0.0)
        if weight <= 0:
            continue
        component_scores[signal.signal_name] = round(signal.strength_score, 2)
        score_sum += signal.strength_score * weight
        weight_sum += weight

    if weight_sum == 0:
        return 50.0, "Yellow", component_scores, 35.0

    score = score_sum / weight_sum
    confidence = min(100.0, 45.0 + (weight_sum * 55.0))
    return round(score, 2), map_score_to_label(score), component_scores, round(confidence, 2)


def score_change(current: float, prior: float | None) -> float | None:
    if prior is None:
        return None
    return round(current - prior, 2)

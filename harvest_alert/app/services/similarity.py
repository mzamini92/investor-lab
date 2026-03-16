from __future__ import annotations

from typing import Any

from harvest_alert.app.models import ReplacementSecurity
from harvest_alert.app.utils.constants import SIMILARITY_WEIGHTS
from harvest_alert.app.utils.math_utils import clamp


def _match_score(left: str | None, right: str | None) -> float:
    if left is None or right is None:
        return 0.5
    return 1.0 if str(left).lower() == str(right).lower() else 0.0


def compute_similarity(
    original: ReplacementSecurity,
    candidate: ReplacementSecurity,
) -> tuple[float, str, list[str]]:
    score = 0.0
    drift: list[str] = []

    score += _match_score(original.asset_class, candidate.asset_class) * SIMILARITY_WEIGHTS["asset_class"]
    score += _match_score(original.region, candidate.region) * SIMILARITY_WEIGHTS["region"]
    score += _match_score(original.market_cap_focus, candidate.market_cap_focus) * SIMILARITY_WEIGHTS["market_cap_focus"]
    score += _match_score(original.style, candidate.style) * SIMILARITY_WEIGHTS["style"]
    score += _match_score(original.factor_tilt, candidate.factor_tilt) * SIMILARITY_WEIGHTS["factor_tilt"]
    score += _match_score(original.benchmark_index, candidate.benchmark_index) * SIMILARITY_WEIGHTS["benchmark_index"]

    shared_tags = len(set(original.strategy_tags) & set(candidate.strategy_tags))
    tag_score = shared_tags / max(len(set(original.strategy_tags)), 1)
    score += tag_score * SIMILARITY_WEIGHTS["strategy_tags"]

    if original.region != candidate.region:
        drift.append("Region exposure differs from the original fund.")
    if original.market_cap_focus != candidate.market_cap_focus:
        drift.append("Market-cap focus changes slightly.")
    if original.style != candidate.style:
        drift.append("Style exposure is not identical.")
    if original.factor_tilt != candidate.factor_tilt and candidate.factor_tilt is not None:
        drift.append("Factor tilt is somewhat different.")

    if not drift:
        summary = "Very similar strategic exposure with low expected drift."
    elif len(drift) == 1:
        summary = drift[0]
    else:
        summary = " ".join(drift[:2])

    return round(clamp(score * 100.0, 0.0, 100.0), 2), summary, drift

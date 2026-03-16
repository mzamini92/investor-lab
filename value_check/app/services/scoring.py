from __future__ import annotations

from typing import Any

from value_check.app.utils.constants import YIELD_METRICS


def compute_composite_score(
    historical_rows: list[dict[str, Any]],
    peer_rows: list[dict[str, Any]],
    current_metrics: dict[str, Any],
) -> tuple[float, float, list[str]]:
    score_components: list[float] = []
    reasons: list[str] = []

    hist_map = {row["metric"]: row for row in historical_rows}
    peer_map = {row["metric"]: row for row in peer_rows}

    for metric, row in hist_map.items():
        percentile = row.get("percentile_rank")
        if percentile is None:
            continue
        score_components.append(float(percentile))
        if percentile >= 80:
            reasons.append(f"{metric} is rich versus its own history.")
        elif percentile <= 20:
            reasons.append(f"{metric} is inexpensive versus its own history.")

    for metric, row in peer_map.items():
        prem_disc = row.get("premium_discount_vs_peer_median")
        if prem_disc is None:
            continue
        translated = 50.0 + (float(prem_disc) * 100.0)
        if metric in YIELD_METRICS:
            translated = 50.0 - (float(prem_disc) * 100.0)
        translated = max(0.0, min(translated, 100.0))
        score_components.append(translated)
        if prem_disc >= 0.2 and metric not in YIELD_METRICS:
            reasons.append(f"{metric} trades at a notable premium to peers.")
        elif prem_disc <= -0.15 and metric not in YIELD_METRICS:
            reasons.append(f"{metric} trades at a discount to peers.")

    spread = current_metrics.get("treasury_relative_fcf_spread")
    if spread is not None:
        if spread <= -0.02:
            score_components.append(80.0)
            reasons.append("Free cash flow yield sits well below the Treasury yield.")
        elif spread >= 0.01:
            score_components.append(25.0)
            reasons.append("Free cash flow yield compares reasonably well with Treasury yields.")
        else:
            score_components.append(50.0)

    if not score_components:
        return 50.0, 35.0, ["Metric coverage is limited, so the verdict has lower confidence."]

    composite = sum(score_components) / len(score_components)
    confidence = min(100.0, 40.0 + (len(score_components) * 8.0))
    return round(composite, 2), round(confidence, 2), reasons

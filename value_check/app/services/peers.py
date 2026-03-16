from __future__ import annotations

from typing import Any

import pandas as pd

from value_check.app.utils.constants import MULTIPLE_METRICS, YIELD_METRICS
from value_check.app.utils.math_utils import premium_discount


def compare_against_peers(current_metrics: dict[str, Any], peer_df: pd.DataFrame, peer_group_name: str) -> list[dict[str, Any]]:
    if peer_df.empty:
        return []
    rows: list[dict[str, Any]] = []
    for metric in MULTIPLE_METRICS + YIELD_METRICS:
        if metric not in peer_df.columns:
            continue
        series = pd.to_numeric(peer_df[metric], errors="coerce").dropna()
        current_value = current_metrics.get(metric)
        if current_value is None or series.empty:
            rows.append(
                {
                    "metric": metric,
                    "peer_group": peer_group_name,
                    "peer_median": None,
                    "peer_q1": None,
                    "peer_q3": None,
                    "premium_discount_vs_peer_median": None,
                    "peer_percentile": None,
                    "peer_interpretation": "insufficient data",
                }
            )
            continue
        peer_median = float(series.median())
        prem_disc = premium_discount(float(current_value), peer_median)
        invert = metric in YIELD_METRICS
        percentile = float((series >= current_value).mean() * 100.0) if invert else float((series <= current_value).mean() * 100.0)
        if prem_disc is not None and prem_disc >= 0.25:
            interpretation = "premium"
        elif prem_disc is not None and prem_disc <= -0.15:
            interpretation = "discount"
        else:
            interpretation = "near peer median"
        rows.append(
            {
                "metric": metric,
                "peer_group": peer_group_name,
                "peer_median": round(peer_median, 6),
                "peer_q1": round(float(series.quantile(0.25)), 6),
                "peer_q3": round(float(series.quantile(0.75)), 6),
                "premium_discount_vs_peer_median": None if prem_disc is None else round(prem_disc, 6),
                "peer_percentile": round(percentile, 2),
                "peer_interpretation": interpretation,
            }
        )
    return rows

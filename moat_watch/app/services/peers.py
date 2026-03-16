from __future__ import annotations

from typing import Any

import pandas as pd

from moat_watch.app.models import QuarterlyMetrics
from moat_watch.app.services.normalization import build_quarter_context


PEER_METRIC_MAP = {
    "gross_margin": "gross_margin",
    "roic_wacc_spread": "roic_wacc_spread",
    "r_and_d_as_pct_revenue": "r_and_d_as_pct_revenue",
    "market_share_change_qoq": "market_share_change_qoq",
    "price_realization": "price_realization",
}


def compare_against_peers(
    context: dict[str, Any],
    peer_df: pd.DataFrame,
) -> list[dict[str, Any]]:
    if peer_df.empty:
        return []

    rows: list[dict[str, Any]] = []
    normalized_rows = []
    for _, row in peer_df.iterrows():
        payload = row.to_dict()
        payload.pop("quarter_label", None)
        payload.pop("quarter_sort", None)
        peer_context = build_quarter_context(
            current=QuarterlyMetrics(**{k: (None if pd.isna(v) else v) for k, v in payload.items()}),
            prior_quarter=None,
            prior_year_quarter=None,
        )
        normalized_rows.append(peer_context)
    peer_context_df = pd.DataFrame(normalized_rows)

    for metric, context_key in PEER_METRIC_MAP.items():
        current_value = context.get(context_key)
        series = pd.to_numeric(peer_context_df[context_key], errors="coerce").dropna() if context_key in peer_context_df.columns else pd.Series(dtype=float)
        if current_value is None or series.empty:
            rows.append(
                {
                    "metric": metric,
                    "current_value": current_value,
                    "peer_median": None,
                    "peer_percentile": None,
                    "premium_discount_vs_peer_median": None,
                    "peer_interpretation": "insufficient data",
                }
            )
            continue
        peer_median = float(series.median())
        percentile = float((series <= current_value).mean() * 100.0)
        premium_discount = None if peer_median == 0 else (float(current_value) / peer_median) - 1.0
        interpretation = "near peer median"
        if premium_discount is not None and premium_discount >= 0.10:
            interpretation = "stronger than peers"
        elif premium_discount is not None and premium_discount <= -0.10:
            interpretation = "weaker than peers"
        rows.append(
            {
                "metric": metric,
                "current_value": round(float(current_value), 6),
                "peer_median": round(peer_median, 6),
                "peer_percentile": round(percentile, 2),
                "premium_discount_vs_peer_median": None if premium_discount is None else round(premium_discount, 6),
                "peer_interpretation": interpretation,
            }
        )
    return rows

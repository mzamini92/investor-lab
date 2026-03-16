from __future__ import annotations

from typing import Any

import pandas as pd

from value_check.app.utils.constants import MULTIPLE_METRICS, YIELD_METRICS


def _expensive_percentile(current: float, series: pd.Series, *, invert: bool = False) -> float:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return 50.0
    if invert:
        return float((clean >= current).mean() * 100.0)
    return float((clean <= current).mean() * 100.0)


def compare_against_history(current_metrics: dict[str, Any], history_df: pd.DataFrame, lookback_years: int) -> list[dict[str, Any]]:
    if history_df.empty:
        return []
    history_df = history_df.copy()
    if "date" in history_df.columns:
        history_df["date"] = pd.to_datetime(history_df["date"])
        latest = history_df["date"].max()
        cutoff = latest - pd.DateOffset(years=lookback_years)
        history_df = history_df.loc[history_df["date"] >= cutoff]

    rows: list[dict[str, Any]] = []
    for metric in MULTIPLE_METRICS + YIELD_METRICS:
        current_value = current_metrics.get(metric)
        raw_series = history_df[metric] if metric in history_df.columns else pd.Series(dtype=float)
        series = pd.to_numeric(raw_series, errors="coerce").dropna()
        if current_value is None or series.empty:
            rows.append(
                {
                    "metric": metric,
                    "current_value": current_value,
                    "historical_average": None,
                    "historical_median": None,
                    "historical_min": None,
                    "historical_max": None,
                    "percentile_rank": None,
                    "metric_interpretation": "insufficient data",
                }
            )
            continue
        invert = metric in YIELD_METRICS
        percentile = _expensive_percentile(float(current_value), series, invert=invert)
        if percentile >= 85:
            interpretation = "expensive"
        elif percentile >= 65:
            interpretation = "slightly expensive"
        elif percentile <= 15:
            interpretation = "cheap"
        elif percentile <= 35:
            interpretation = "slightly cheap"
        else:
            interpretation = "fair"
        rows.append(
            {
                "metric": metric,
                "current_value": round(float(current_value), 6),
                "historical_average": round(float(series.mean()), 6),
                "historical_median": round(float(series.median()), 6),
                "historical_min": round(float(series.min()), 6),
                "historical_max": round(float(series.max()), 6),
                "percentile_rank": round(percentile, 2),
                "metric_interpretation": interpretation,
            }
        )
    return rows

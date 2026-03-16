from __future__ import annotations

from typing import Any

import pandas as pd


def distribution_gap(left: dict[str, float], right: dict[str, float]) -> float:
    categories = set(left) | set(right)
    return 0.5 * sum(abs(left.get(category, 0.0) - right.get(category, 0.0)) for category in categories)


def compute_economic_reality_gap(
    *,
    normalized_portfolio: list[dict[str, Any]],
    label_region_mix: dict[str, float],
    revenue_exposure_df: pd.DataFrame,
    dependency_metrics: dict[str, Any],
    region_metrics: dict[str, Any],
    currency_exposure_df: pd.DataFrame,
) -> float:
    perceived_diversification = (
        0.40 * min(len(normalized_portfolio) / 6.0, 1.0)
        + 0.35 * min(len(label_region_mix) / 4.0, 1.0)
        + 0.25 * min((1.0 / max(sum(weight * weight for weight in label_region_mix.values()), 1e-9)) / 4.0, 1.0)
    )
    revenue_mix = {str(row["name"]): float(row["exposure"]) for _, row in revenue_exposure_df.iterrows()}
    label_gap = distribution_gap(label_region_mix, revenue_mix)
    actual_concentration = (
        0.35 * float(dependency_metrics["hhi"])
        + 0.25 * float(region_metrics["hhi"])
        + 0.20 * float(dependency_metrics["top_3_concentration"])
        + 0.20 * float(currency_exposure_df["exposure"].head(1).sum())
    )
    score = ((0.55 * actual_concentration) + (0.25 * label_gap) + (0.20 * (1.0 - perceived_diversification))) * 100.0
    return round(max(0.0, min(score, 100.0)), 2)


def compute_global_diversification_score(
    *,
    country_metrics: dict[str, Any],
    region_metrics: dict[str, Any],
    revenue_metrics: dict[str, Any],
    dependency_metrics: dict[str, Any],
    currency_metrics: dict[str, Any],
    country_exposure_df: pd.DataFrame,
    currency_exposure_df: pd.DataFrame,
) -> tuple[float, dict[str, float]]:
    us_exposure = float(country_exposure_df.loc[country_exposure_df["name"] == "United States", "exposure"].sum())
    usd_exposure = float(currency_exposure_df.loc[currency_exposure_df["name"] == "USD", "exposure"].sum())

    penalties = {
        "country_penalty": (1.0 - min(float(country_metrics["effective_count"]) / 8.0, 1.0)) * 22.0,
        "region_penalty": (1.0 - min(float(region_metrics["effective_count"]) / 4.0, 1.0)) * 14.0,
        "revenue_penalty": (1.0 - min(float(revenue_metrics["effective_count"]) / 5.0, 1.0)) * 14.0,
        "dependency_penalty": (1.0 - min(float(dependency_metrics["effective_count"]) / 8.0, 1.0)) * 20.0,
        "currency_penalty": (1.0 - min(float(currency_metrics["effective_count"]) / 4.0, 1.0)) * 10.0,
        "us_penalty": us_exposure * 12.0,
        "usd_penalty": usd_exposure * 8.0,
        "top_dependency_penalty": float(dependency_metrics["top_concentration"]) * 12.0,
    }
    score = 100.0 - sum(penalties.values())
    return round(max(0.0, min(score, 100.0)), 2), {key: round(value, 2) for key, value in penalties.items()}


def compute_macro_dependence_score(dependency_metrics: dict[str, Any]) -> tuple[float, dict[str, float]]:
    concentration = float(dependency_metrics["top_5_concentration"])
    hhi = float(dependency_metrics["hhi"])
    effective_count_gap = 1.0 - min(float(dependency_metrics["effective_count"]) / 8.0, 1.0)
    raw_score = (0.45 * concentration) + (0.35 * hhi) + (0.20 * effective_count_gap)
    score = max(0.0, min(raw_score * 100.0, 100.0))
    breakdown = {
        "concentration_component": round(concentration * 45.0, 2),
        "hhi_component": round(hhi * 35.0, 2),
        "effective_count_component": round(effective_count_gap * 20.0, 2),
    }
    return round(score, 2), breakdown

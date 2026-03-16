from __future__ import annotations

from typing import Any

import pandas as pd


def _distribution_gap(label_mix: dict[str, float], actual_mix_df: pd.DataFrame) -> float:
    actual_mix = {str(row["name"]): float(row["exposure"]) for _, row in actual_mix_df.iterrows()}
    regions = set(label_mix) | set(actual_mix)
    return 0.5 * sum(abs(label_mix.get(region, 0.0) - actual_mix.get(region, 0.0)) for region in regions)


def compute_economic_reality_gap(
    *,
    label_region_mix: dict[str, float],
    actual_region_exposure_df: pd.DataFrame,
    domicile_vs_revenue_df: pd.DataFrame,
    region_hhi: float,
) -> float:
    label_gap = _distribution_gap(label_region_mix, actual_region_exposure_df)
    revenue_gap = float(domicile_vs_revenue_df["absolute_gap"].sum()) * 0.5 if not domicile_vs_revenue_df.empty else 0.0
    concentration_penalty = min(region_hhi, 1.0)
    score = ((0.50 * label_gap) + (0.35 * revenue_gap) + (0.15 * concentration_penalty)) * 100.0
    return round(max(0.0, min(score, 100.0)), 2)


def compute_global_dependence_score(
    *,
    country_metrics: dict[str, Any],
    region_metrics: dict[str, Any],
    currency_exposure_df: pd.DataFrame,
    market_cap_exposure_df: pd.DataFrame,
    country_exposure_df: pd.DataFrame,
    economic_reality_gap: float,
) -> tuple[float, dict[str, float]]:
    us_exposure = float(country_exposure_df.loc[country_exposure_df["name"] == "United States", "exposure"].sum())
    north_america_exposure = float(region_metrics.get("top_region_exposure", 0.0)) if region_metrics.get("top_region") == "North America" else 0.0
    usd_exposure = float(currency_exposure_df.loc[currency_exposure_df["name"] == "USD", "exposure"].sum())
    mega_cap_exposure = float(market_cap_exposure_df.loc[market_cap_exposure_df["name"] == "Mega Cap", "exposure"].sum())

    effective_countries = float(country_metrics["effective_count"])
    effective_regions = float(region_metrics["effective_count"])
    country_diversity_reward = min(effective_countries / 10.0, 1.0) * 30.0
    region_diversity_reward = min(effective_regions / 4.0, 1.0) * 20.0
    concentration_penalty = min(float(country_metrics["top_5_concentration"]), 1.0) * 20.0
    us_penalty = us_exposure * 12.0
    north_america_penalty = north_america_exposure * 10.0
    usd_penalty = usd_exposure * 8.0
    mega_cap_penalty = mega_cap_exposure * 7.0
    reality_gap_penalty = (economic_reality_gap / 100.0) * 13.0

    raw_score = (
        25.0
        + country_diversity_reward
        + region_diversity_reward
        - concentration_penalty
        - us_penalty
        - north_america_penalty
        - usd_penalty
        - mega_cap_penalty
        - reality_gap_penalty
    )
    breakdown = {
        "country_diversity_reward": round(country_diversity_reward, 2),
        "region_diversity_reward": round(region_diversity_reward, 2),
        "concentration_penalty": round(concentration_penalty, 2),
        "us_penalty": round(us_penalty, 2),
        "north_america_penalty": round(north_america_penalty, 2),
        "usd_penalty": round(usd_penalty, 2),
        "mega_cap_penalty": round(mega_cap_penalty, 2),
        "reality_gap_penalty": round(reality_gap_penalty, 2),
    }
    return round(max(0.0, min(raw_score, 100.0)), 2), breakdown


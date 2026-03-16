from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd


def compute_concentration_metrics(underlying_exposures: pd.DataFrame) -> dict[str, Any]:
    exposures = underlying_exposures["exposure"].to_numpy(dtype=float)
    hhi = float(np.square(exposures).sum()) if len(exposures) else 0.0
    effective_number = float(1.0 / hhi) if hhi > 0 else 0.0

    return {
        "underlying_company_count": int(len(underlying_exposures)),
        "top_5_concentration": round(float(exposures[:5].sum()), 6),
        "top_8_concentration": round(float(exposures[:8].sum()), 6),
        "top_10_concentration": round(float(exposures[:10].sum()), 6),
        "top_20_concentration": round(float(exposures[:20].sum()), 6),
        "hhi": round(hhi, 6),
        "effective_number_of_stocks": round(effective_number, 6),
    }


def compute_dimension_hhi(exposure_df: pd.DataFrame) -> tuple[float, float]:
    weights = exposure_df["exposure"].to_numpy(dtype=float)
    hhi = float(np.square(weights).sum()) if len(weights) else 0.0
    effective_count = float(1.0 / hhi) if hhi > 0 else 0.0
    return round(hhi, 6), round(effective_count, 6)


def compute_portfolio_redundancy_index(
    overlap_pairs: list[dict[str, Any]],
    portfolio_weights: dict[str, float],
) -> float:
    if not overlap_pairs:
        return 0.0

    weighted_sum = 0.0
    importance_sum = 0.0
    for pair in overlap_pairs:
        importance = portfolio_weights[pair["etf_a"]] * portfolio_weights[pair["etf_b"]]
        weighted_sum += importance * float(pair["weighted_overlap"])
        importance_sum += importance
    if importance_sum == 0:
        return 0.0
    return round(100.0 * (weighted_sum / importance_sum), 2)


def compute_hidden_concentration_score(
    effective_number_of_stocks: float,
    naive_holdings_count: int,
    top_10_concentration: float,
    sector_hhi: float,
    redundancy_index: float,
    practical_overlap_total: float,
) -> float:
    duplication_gap = 1.0 - min(effective_number_of_stocks / max(naive_holdings_count, 1), 1.0)
    redundancy_component = min(redundancy_index / 100.0, 1.0)
    practical_component = min(practical_overlap_total, 1.0)

    raw_score = (
        (0.40 * duplication_gap)
        + (0.25 * top_10_concentration)
        + (0.20 * redundancy_component)
        + (0.10 * sector_hhi)
        + (0.05 * practical_component)
    )
    return round(max(0.0, min(raw_score, 1.0)) * 100.0, 2)


def compute_diversification_score(
    top_10_concentration: float,
    sector_effective_count: float,
    country_effective_count: float,
    style_effective_count: float,
    effective_number_of_stocks: float,
    naive_holdings_count: int,
    redundancy_index: float,
) -> tuple[float, dict[str, float]]:
    duplicate_holdings_penalty = (1.0 - min(effective_number_of_stocks / max(naive_holdings_count, 1), 1.0)) * 35.0
    top_10_penalty = min(max((top_10_concentration - 0.20) / 0.50, 0.0), 1.0) * 25.0
    sector_penalty = (1.0 - min(sector_effective_count / 6.0, 1.0)) * 15.0
    geography_penalty = (1.0 - min(country_effective_count / 4.0, 1.0)) * 15.0
    style_penalty = (1.0 - min(style_effective_count / 4.0, 1.0)) * 10.0
    redundancy_penalty = min(redundancy_index / 100.0, 1.0) * 10.0

    penalties = {
        "duplicate_holdings_penalty": round(duplicate_holdings_penalty, 2),
        "top_10_penalty": round(top_10_penalty, 2),
        "sector_penalty": round(sector_penalty, 2),
        "geography_penalty": round(geography_penalty, 2),
        "style_penalty": round(style_penalty, 2),
        "redundancy_penalty": round(redundancy_penalty, 2),
    }
    score = 100.0 - sum(penalties.values())
    return round(max(0.0, min(score, 100.0)), 2), penalties


def format_pct(value: float) -> str:
    return f"{value:.1%}"


def safe_ratio(numerator: float, denominator: float) -> float:
    if math.isclose(denominator, 0.0):
        return 0.0
    return numerator / denominator


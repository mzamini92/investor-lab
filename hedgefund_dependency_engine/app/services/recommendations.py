from __future__ import annotations

from typing import Any


def generate_recommendations(
    *,
    normalized_portfolio: list[dict[str, Any]],
    dependency_exposures: list[dict[str, Any]],
    country_exposures: list[dict[str, Any]],
    currency_exposures: list[dict[str, Any]],
    overlap_pairs: list[dict[str, Any]],
    diversification_scores: dict[str, float],
) -> list[str]:
    recommendations: list[str] = []
    tickers = {row["ticker"] for row in normalized_portfolio}
    if dependency_exposures and dependency_exposures[0]["dependency_name"] in {"ai_capex", "cloud_spending", "global_semiconductors"}:
        recommendations.append("Reduce AI-capex dependence by complementing growth-heavy funds with sectors linked to different economic engines.")
    if country_exposures and country_exposures[0]["name"] == "United States" and float(country_exposures[0]["exposure"]) >= 0.50:
        recommendations.append("Add broader ex-US diversification if your goal is lower dependence on the U.S. economy.")
    if currency_exposures and currency_exposures[0]["name"] == "USD" and float(currency_exposures[0]["exposure"]) >= 0.60:
        recommendations.append("Increase non-USD exposure to reduce sensitivity to a single currency regime.")
    for pair in overlap_pairs:
        if float(pair["weighted_overlap"]) >= 0.75:
            recommendations.append(f"Trim one of {pair['etf_a']} or {pair['etf_b']} to reduce redundant look-through exposure.")
            break
    if "QQQ" in tickers and "VTI" in tickers:
        recommendations.append("QQQ and VTI stack U.S. mega-cap growth and AI sensitivity; verify both are intentional at current weights.")
    if float(diversification_scores["global_diversification_score"]) <= 50:
        recommendations.append("Favor more complementary drivers, regions, and currencies instead of adding another overlapping broad U.S. fund.")
    return recommendations

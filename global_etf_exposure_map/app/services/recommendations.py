from __future__ import annotations

from typing import Any


def generate_recommendations(
    *,
    country_exposure_table: list[dict[str, Any]],
    region_exposure_table: list[dict[str, Any]],
    currency_exposure_table: list[dict[str, Any]],
    normalized_portfolio: list[dict[str, Any]],
    global_dependence_score: float,
) -> list[str]:
    recommendations: list[str] = []
    tickers = {row["ticker"] for row in normalized_portfolio}

    if country_exposure_table and country_exposure_table[0]["name"] == "United States" and float(country_exposure_table[0]["exposure"]) >= 0.50:
        recommendations.append("Increase true ex-U.S. diversification if your goal is lower dependence on the U.S. economy.")

    if region_exposure_table and float(region_exposure_table[0]["exposure"]) >= 0.60:
        recommendations.append("Add underrepresented regions to reduce single-region dependence and improve resilience.")

    if currency_exposure_table and currency_exposure_table[0]["name"] == "USD" and float(currency_exposure_table[0]["exposure"]) >= 0.60:
        recommendations.append("Consider adding non-USD exposure if you want less sensitivity to one currency regime.")

    if "QQQ" in tickers and "VTI" in tickers:
        recommendations.append("QQQ and VTI can stack U.S. mega-cap growth exposure; review whether both allocations are needed at current sizes.")

    if "ARKK" in tickers:
        recommendations.append("If ARKK is a satellite holding, pair it with broader non-U.S. or value-oriented exposures to balance its concentration profile.")

    if global_dependence_score <= 45:
        recommendations.append("Favor broader geographic complements such as diversified ex-U.S. or emerging-market funds over adding more U.S.-heavy growth exposure.")

    return recommendations


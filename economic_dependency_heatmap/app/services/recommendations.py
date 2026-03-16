from __future__ import annotations

from typing import Any


def generate_recommendations(
    *,
    normalized_portfolio: list[dict[str, Any]],
    country_exposure_table: list[dict[str, Any]],
    revenue_exposure_table: list[dict[str, Any]],
    currency_exposure_table: list[dict[str, Any]],
    macro_dependency_exposure_table: list[dict[str, Any]],
    diversification_scores: dict[str, float],
) -> list[str]:
    recommendations: list[str] = []
    tickers = {row["ticker"] for row in normalized_portfolio}

    if country_exposure_table and country_exposure_table[0]["name"] == "United States" and float(country_exposure_table[0]["exposure"]) >= 0.50:
        recommendations.append("Reduce U.S.-heavy overlap or add holdings with stronger true non-U.S. revenue exposure.")
    if revenue_exposure_table and revenue_exposure_table[0]["name"] == "United States" and float(revenue_exposure_table[0]["exposure"]) >= 0.45:
        recommendations.append("Add companies or ETFs whose revenue base is less tied to U.S. demand if you want more economic diversification.")
    if macro_dependency_exposure_table and macro_dependency_exposure_table[0]["dependency_name"] in {"ai_capex", "cloud_spending", "global_semiconductors"}:
        recommendations.append("AI and cloud exposure is dominant. Pair growth-heavy allocations with sectors less tied to the same capital-spending engine.")
    if currency_exposure_table and currency_exposure_table[0]["name"] == "USD" and float(currency_exposure_table[0]["exposure"]) >= 0.60:
        recommendations.append("Add non-USD exposure if you want less dependence on one currency regime.")
    if "QQQ" in tickers and "VTI" in tickers:
        recommendations.append("QQQ and VTI stack U.S. mega-cap growth sensitivity. Check whether both are needed at current sizes.")
    if float(diversification_scores["global_diversification_score"]) <= 50:
        recommendations.append("Focus on complementary, genuinely different economic engines rather than adding more ETFs with the same macro profile.")
    return recommendations

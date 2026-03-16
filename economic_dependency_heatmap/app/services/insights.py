from __future__ import annotations

from typing import Any


def generate_warnings(
    *,
    normalized_portfolio: list[dict[str, Any]],
    country_exposure_table: list[dict[str, Any]],
    revenue_exposure_table: list[dict[str, Any]],
    macro_dependency_exposure_table: list[dict[str, Any]],
    diversification_scores: dict[str, float],
    concentration_metrics: dict[str, Any],
) -> list[str]:
    warnings: list[str] = []
    if country_exposure_table and float(country_exposure_table[0]["exposure"]) >= 0.50:
        warnings.append(
            f"You own {len(normalized_portfolio)} ETFs, but {float(country_exposure_table[0]['exposure']):.1%} of your portfolio still depends on {country_exposure_table[0]['name']}."
        )
    if revenue_exposure_table and float(revenue_exposure_table[0]["exposure"]) >= 0.45:
        warnings.append(
            f"Revenue concentration is high: {revenue_exposure_table[0]['name']} drives {float(revenue_exposure_table[0]['exposure']):.1%} of the portfolio's economic footprint."
        )
    if macro_dependency_exposure_table and float(macro_dependency_exposure_table[0]["exposure"]) >= 0.35:
        warnings.append(
            f"Your top hidden macro driver is {macro_dependency_exposure_table[0]['display_name']} at {float(macro_dependency_exposure_table[0]['exposure']):.1%}."
        )
    if float(concentration_metrics["dependency"]["top_3_concentration"]) >= 0.55:
        warnings.append(
            f"The top 3 economic drivers explain {float(concentration_metrics['dependency']['top_3_concentration']):.1%} of hidden dependency."
        )
    if float(diversification_scores["economic_reality_gap"]) >= 45:
        warnings.append(
            f"Economic Reality Gap is elevated at {float(diversification_scores['economic_reality_gap']):.1f}/100, meaning ETF labels overstate diversification."
        )
    if float(diversification_scores["global_diversification_score"]) <= 50:
        warnings.append(
            f"Global Diversification Score is only {float(diversification_scores['global_diversification_score']):.1f}/100."
        )
    return warnings


def generate_summary_insights(
    *,
    country_exposure_table: list[dict[str, Any]],
    region_exposure_table: list[dict[str, Any]],
    revenue_exposure_table: list[dict[str, Any]],
    macro_dependency_exposure_table: list[dict[str, Any]],
    diversification_scores: dict[str, float],
    concentration_metrics: dict[str, Any],
) -> list[str]:
    insights = [
        f"Global Diversification Score: {float(diversification_scores['global_diversification_score']):.1f}/100.",
        f"Economic Reality Gap: {float(diversification_scores['economic_reality_gap']):.1f}/100.",
        f"Macro Dependence Score: {float(diversification_scores['macro_dependence_score']):.1f}/100.",
        f"Effective macro drivers: {float(concentration_metrics['dependency']['effective_count']):.2f}.",
    ]
    if country_exposure_table:
        insights.append(
            f"Top country exposure is {country_exposure_table[0]['name']} at {float(country_exposure_table[0]['exposure']):.1%}."
        )
    if revenue_exposure_table:
        insights.append(
            f"Top revenue demand center is {revenue_exposure_table[0]['name']} at {float(revenue_exposure_table[0]['exposure']):.1%}."
        )
    if macro_dependency_exposure_table:
        insights.append(
            f"Top macro dependency is {macro_dependency_exposure_table[0]['display_name']} at {float(macro_dependency_exposure_table[0]['exposure']):.1%}."
        )
    if region_exposure_table:
        insights.append(
            f"Top region exposure is {region_exposure_table[0]['name']} at {float(region_exposure_table[0]['exposure']):.1%}."
        )
    return insights

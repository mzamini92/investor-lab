from __future__ import annotations

from typing import Any


def generate_warnings(
    *,
    normalized_portfolio: list[dict[str, Any]],
    country_exposure_table: list[dict[str, Any]],
    region_exposure_table: list[dict[str, Any]],
    currency_exposure_table: list[dict[str, Any]],
    country_metrics: dict[str, Any],
    global_dependence_score: float,
    economic_reality_gap: float,
) -> list[str]:
    warnings: list[str] = []

    if country_exposure_table:
        top_country = country_exposure_table[0]
        if float(top_country["exposure"]) >= 0.50:
            warnings.append(
                f"You own {len(normalized_portfolio)} ETFs, but {float(top_country['exposure']):.1%} of your portfolio is effectively exposed to {top_country['name']}."
            )

    if region_exposure_table:
        top_region = region_exposure_table[0]
        if float(top_region["exposure"]) >= 0.55:
            warnings.append(
                f"Regional dependence is high: {top_region['name']} accounts for {float(top_region['exposure']):.1%} of underlying exposure."
            )

    if currency_exposure_table:
        top_currency = currency_exposure_table[0]
        if float(top_currency["exposure"]) >= 0.55:
            warnings.append(
                f"{top_currency['name']}-linked exposure is materially larger than many investors expect at {float(top_currency['exposure']):.1%}."
            )

    if float(country_metrics["top_5_concentration"]) >= 0.75:
        warnings.append(
            f"Your top 5 countries drive {float(country_metrics['top_5_concentration']):.1%} of exposure, which limits true geographic diversification."
        )

    if economic_reality_gap >= 30:
        warnings.append(
            f"Your portfolio appears more diversified by ETF labels than by underlying exposure. Economic Reality Gap: {economic_reality_gap:.1f}/100."
        )

    if global_dependence_score <= 45:
        warnings.append(
            f"Global Dependence Score is only {global_dependence_score:.1f}/100, indicating concentrated economic exposure."
        )

    return warnings


def generate_summary_insights(
    *,
    country_exposure_table: list[dict[str, Any]],
    region_exposure_table: list[dict[str, Any]],
    currency_exposure_table: list[dict[str, Any]],
    country_metrics: dict[str, Any],
    region_metrics: dict[str, Any],
    global_dependence_score: float,
    economic_reality_gap: float,
) -> list[str]:
    insights = [
        f"Global Dependence Score: {global_dependence_score:.1f}/100.",
        f"Economic Reality Gap: {economic_reality_gap:.1f}/100.",
        f"Effective countries: {float(country_metrics['effective_count']):.2f}.",
        f"Effective regions: {float(region_metrics['effective_count']):.2f}.",
    ]
    if country_exposure_table:
        insights.append(
            f"Top country exposure is {country_exposure_table[0]['name']} at {float(country_exposure_table[0]['exposure']):.1%}."
        )
    if region_exposure_table:
        insights.append(
            f"Top region exposure is {region_exposure_table[0]['name']} at {float(region_exposure_table[0]['exposure']):.1%}."
        )
    if currency_exposure_table:
        insights.append(
            f"Top currency exposure is {currency_exposure_table[0]['name']} at {float(currency_exposure_table[0]['exposure']):.1%}."
        )
    return insights


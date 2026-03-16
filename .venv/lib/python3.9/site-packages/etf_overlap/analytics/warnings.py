from __future__ import annotations

from typing import Any


def generate_warnings(
    *,
    naive_holdings_count: int,
    concentration_metrics: dict[str, Any],
    sector_exposures: list[dict[str, Any]],
    country_exposures: list[dict[str, Any]],
    overlap_pairs: list[dict[str, Any]],
    mag7_exposure: dict[str, Any],
    hidden_concentration_score: float,
    diversification_score: float,
) -> list[str]:
    warnings: list[str] = []

    top_8 = float(concentration_metrics["top_8_concentration"])
    top_10 = float(concentration_metrics["top_10_concentration"])
    effective_number = float(concentration_metrics["effective_number_of_stocks"])
    if top_8 >= 0.30:
        warnings.append(
            f"You think you own {naive_holdings_count} stocks, but {top_8:.1%} of your portfolio is concentrated in the top 8 companies."
        )

    if effective_number < 20:
        warnings.append(
            f"Your effective number of stocks is only {effective_number:.1f}, which is much lower than the headline ETF holding counts suggest."
        )

    for pair in overlap_pairs:
        if float(pair["weighted_overlap"]) >= 0.70 and float(pair["practical_overlap_contribution"]) >= 0.10:
            warnings.append(
                f"{pair['etf_a']} and {pair['etf_b']} are highly redundant in your portfolio with {float(pair['weighted_overlap']):.1%} weighted overlap."
            )

    if sector_exposures:
        top_sector = sector_exposures[0]
        if top_sector["name"] == "Technology" and float(top_sector["exposure"]) >= 0.30:
            warnings.append(
                f"Your actual tech exposure is materially higher than you may expect at {float(top_sector['exposure']):.1%}."
            )

    if country_exposures:
        top_country = country_exposures[0]
        if float(top_country["exposure"]) >= 0.75:
            warnings.append(
                f"Country concentration is elevated: {top_country['name']} represents {float(top_country['exposure']):.1%} of underlying exposure."
            )

    if float(mag7_exposure["total"]) >= 0.25:
        warnings.append(
            f"The Magnificent 7 make up {float(mag7_exposure['total']):.1%} of the portfolio, which can overpower diversification elsewhere."
        )

    if top_10 >= 0.45:
        warnings.append(f"Top-10 concentration is high at {top_10:.1%}, increasing single-name risk.")

    if hidden_concentration_score >= 60:
        warnings.append(
            f"Your hidden concentration score is {hidden_concentration_score:.1f}/100, indicating a misleading diversification picture."
        )

    if diversification_score <= 50:
        warnings.append(
            f"Diversification quality is weak at {diversification_score:.1f}/100 after adjusting for overlap and concentration."
        )

    return warnings


from __future__ import annotations

from typing import Any


def generate_suggestions(
    *,
    overlap_pairs: list[dict[str, Any]],
    sector_exposures: list[dict[str, Any]],
    country_exposures: list[dict[str, Any]],
    mag7_exposure: dict[str, Any],
    concentration_metrics: dict[str, Any],
    normalized_portfolio: list[dict[str, Any]],
) -> list[str]:
    suggestions: list[str] = []
    portfolio_tickers = {row["ticker"] for row in normalized_portfolio}

    for pair in overlap_pairs:
        if float(pair["weighted_overlap"]) >= 0.75:
            suggestions.append(
                f"Consider trimming one of {pair['etf_a']} or {pair['etf_b']} to reduce duplication; the smaller allocation is usually the easiest place to start."
            )
            break

    if float(concentration_metrics["top_10_concentration"]) >= 0.40:
        suggestions.append(
            "Lower top-company concentration by pairing broad U.S. beta exposure with more complementary sleeves such as equal-weight, value, or international equity."
        )

    if country_exposures and float(country_exposures[0]["exposure"]) >= 0.75 and "VXUS" not in portfolio_tickers:
        suggestions.append(
            "International diversification is light. Adding a complementary ex-U.S. ETF such as VXUS can reduce U.S. concentration risk."
        )

    if sector_exposures and sector_exposures[0]["name"] == "Technology" and float(sector_exposures[0]["exposure"]) >= 0.35:
        suggestions.append(
            "Technology dominates the portfolio. Rebalancing toward healthcare, industrials, financials, or international markets can improve factor balance."
        )

    if float(mag7_exposure["total"]) >= 0.30:
        suggestions.append(
            "Magnificent 7 exposure is elevated. If that concentration is unintentional, rebalance into funds with lower mega-cap growth weight."
        )

    if "ARKK" in portfolio_tickers and ("QQQ" in portfolio_tickers or "VUG" in portfolio_tickers):
        suggestions.append(
            "High-growth funds can stack the same style risk. Make sure speculative innovation exposure is sized intentionally alongside core holdings."
        )

    return suggestions


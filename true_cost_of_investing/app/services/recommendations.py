from __future__ import annotations

from typing import Any


def generate_recommendations(
    *,
    holdings: list[dict[str, Any]],
    assumptions: dict[str, Any],
    annual_breakdown: list[dict[str, Any]],
) -> list[str]:
    recommendations: list[str] = []
    high_fee_holdings = [row for row in holdings if row["expense_ratio"] >= 0.005]
    high_turnover_holdings = [row for row in holdings if row["annual_turnover_rate"] >= 0.5]

    if high_fee_holdings:
        tickers = ", ".join(row["ticker"] for row in high_fee_holdings[:3])
        recommendations.append(
            f"Review high-fee holdings such as {tickers}; long holding periods amplify expense ratio drag."
        )
    if assumptions["account_type"] == "taxable" and high_turnover_holdings:
        recommendations.append(
            "High-turnover holdings in taxable accounts can create avoidable tax drag. Consider whether lower-turnover alternatives fit your strategy."
        )
    if assumptions["annual_advisory_fee"] >= 0.0075:
        recommendations.append(
            "A high advisory fee can become one of the biggest lifetime costs. Even modest fee reductions can preserve meaningful wealth."
        )
    if assumptions["annual_cash_drag"] >= 0.0025:
        recommendations.append(
            "Persistent cash drag compounds quietly. Revisit whether idle cash assumptions are higher than necessary."
        )

    biggest_cost = max(annual_breakdown, key=lambda row: row["annual_cost_dollars"])
    if biggest_cost["category"] == "dividend_tax_drag":
        recommendations.append(
            "Taxes appear to be the main hidden drag. Tax-efficient funds and better asset location may matter more than shaving a few basis points of fund fees."
        )
    return recommendations

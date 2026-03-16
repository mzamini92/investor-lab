from __future__ import annotations

from typing import Any


def build_summary(
    *,
    blended_metrics: dict[str, Any],
    annual_breakdown: list[dict[str, Any]],
    projected_ending_values: dict[str, Any],
    dollars_lost_by_category: list[dict[str, Any]],
) -> dict[str, Any]:
    biggest_category = max(dollars_lost_by_category, key=lambda item: item["attributable_ending_value_loss"])
    total_drag_rate = sum(item["annual_rate"] for item in annual_breakdown)
    gross_value = projected_ending_values["gross_ending_value"]
    net_value = projected_ending_values["net_ending_value"]

    return {
        "portfolio_value": blended_metrics["portfolio_value"],
        "total_hidden_annual_drag_rate": round(total_drag_rate, 6),
        "total_hidden_annual_drag_dollars": round(sum(item["annual_cost_dollars"] for item in annual_breakdown), 2),
        "gross_ending_value": gross_value,
        "net_ending_value": net_value,
        "total_30_year_dollars_lost": round(gross_value - net_value, 2),
        "biggest_cost_category": biggest_category["category"],
    }


def generate_insights(summary: dict[str, Any], annual_breakdown: list[dict[str, Any]], assumptions: dict[str, Any]) -> list[str]:
    biggest = max(annual_breakdown, key=lambda item: item["annual_cost_dollars"])
    dollars_lost = summary["total_30_year_dollars_lost"]
    return [
        f"Your modeled annual friction is about {summary['total_hidden_annual_drag_rate']:.2%}, which compounds into roughly ${dollars_lost:,.0f} of lost ending wealth.",
        f"The largest recurring drag today is {biggest['category'].replace('_', ' ')} at about ${biggest['annual_cost_dollars']:,.0f} per year.",
        f"Over a {assumptions['investment_horizon_years']}-year horizon, small percentage drags matter far more than they look in a single year.",
    ]

from __future__ import annotations

from collections import defaultdict
from typing import Any

from true_cost_of_investing.app.models import CategoryAttribution, PortfolioAssumptions, ProjectionPoint
from true_cost_of_investing.app.utils.math_utils import annual_to_monthly_rate


def _run_projection(
    *,
    initial_value: float,
    annual_gross_return: float,
    monthly_contribution: float,
    years: int,
    category_rates: dict[str, float],
    contribution_growth_rate: float,
) -> dict[str, Any]:
    gross_monthly = annual_to_monthly_rate(annual_gross_return)
    monthly_category_rates = {name: annual_to_monthly_rate(-rate) * -1.0 for name, rate in category_rates.items()}
    month_count = years * 12
    gross_value = initial_value
    net_value = initial_value
    annual_contribution = monthly_contribution * 12.0
    category_direct_costs: dict[str, float] = defaultdict(float)
    checkpoints: list[ProjectionPoint] = []

    for month in range(1, month_count + 1):
        current_year = (month - 1) // 12
        monthly_contribution_amount = (annual_contribution * ((1 + contribution_growth_rate) ** current_year)) / 12.0

        gross_value *= 1.0 + gross_monthly
        gross_value += monthly_contribution_amount

        net_value *= 1.0 + gross_monthly
        for category_name, monthly_drag in monthly_category_rates.items():
            drag_dollars = net_value * monthly_drag
            net_value -= drag_dollars
            category_direct_costs[category_name] += drag_dollars
        net_value += monthly_contribution_amount

        if month % 12 == 0:
            year = month // 12
            cumulative_direct_costs = sum(category_direct_costs.values())
            checkpoints.append(
                ProjectionPoint(
                    year=year,
                    gross_value=round(gross_value, 2),
                    net_value=round(net_value, 2),
                    cumulative_direct_costs=round(cumulative_direct_costs, 2),
                    cumulative_lost_wealth=round(gross_value - net_value, 2),
                )
            )

    return {
        "gross_ending_value": round(gross_value, 2),
        "net_ending_value": round(net_value, 2),
        "category_direct_costs": {key: round(value, 2) for key, value in category_direct_costs.items()},
        "timeline": checkpoints,
    }


def build_projection(
    *,
    initial_value: float,
    annual_gross_return: float,
    assumptions: PortfolioAssumptions,
    category_rates: dict[str, float],
) -> dict[str, Any]:
    return _run_projection(
        initial_value=initial_value,
        annual_gross_return=annual_gross_return,
        monthly_contribution=assumptions.monthly_contribution,
        years=assumptions.investment_horizon_years,
        category_rates=category_rates,
        contribution_growth_rate=assumptions.contribution_growth_rate,
    )


def attribute_category_losses(
    *,
    initial_value: float,
    annual_gross_return: float,
    assumptions: PortfolioAssumptions,
    category_rates: dict[str, float],
    base_projection: dict[str, Any],
) -> list[CategoryAttribution]:
    total_loss = max(base_projection["gross_ending_value"] - base_projection["net_ending_value"], 0.0)
    rows: list[CategoryAttribution] = []

    for category_name in category_rates:
        reduced_rates = {key: value for key, value in category_rates.items() if key != category_name}
        reduced_projection = build_projection(
            initial_value=initial_value,
            annual_gross_return=annual_gross_return,
            assumptions=assumptions,
            category_rates=reduced_rates,
        )
        attributable_loss = reduced_projection["net_ending_value"] - base_projection["net_ending_value"]
        rows.append(
            CategoryAttribution(
                category=category_name,
                direct_cost_dollars=base_projection["category_direct_costs"].get(category_name, 0.0),
                attributable_ending_value_loss=round(attributable_loss, 2),
                attributable_percent_of_total_loss=round((attributable_loss / total_loss) if total_loss else 0.0, 6),
            )
        )
    return rows

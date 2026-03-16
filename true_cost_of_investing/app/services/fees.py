from __future__ import annotations

from true_cost_of_investing.app.models import AnnualCostComponent, NormalizedHolding, PortfolioAssumptions


def calculate_fee_costs(
    holdings: list[NormalizedHolding],
    assumptions: PortfolioAssumptions,
    portfolio_value: float,
) -> tuple[list[AnnualCostComponent], list[dict[str, float]]]:
    per_holding: list[dict[str, float]] = []
    expense_cost = 0.0
    layered_cost = 0.0
    advisory_cost = 0.0

    for holding in holdings:
        position_expense = holding.amount * holding.expense_ratio
        position_layered = holding.amount * holding.layered_fee_ratio
        effective_advisory_rate = (
            assumptions.annual_advisory_fee if holding.advisory_fee_override is None else holding.advisory_fee_override
        )
        position_advisory = holding.amount * effective_advisory_rate

        expense_cost += position_expense
        layered_cost += position_layered
        advisory_cost += position_advisory
        per_holding.append(
            {
                "ticker": holding.ticker,
                "expense_ratio_cost": round(position_expense, 2),
                "layered_fee_cost": round(position_layered, 2),
                "advisory_fee_cost": round(position_advisory, 2),
            }
        )

    components = [
        AnnualCostComponent(
            category="expense_ratio",
            annual_rate=expense_cost / portfolio_value,
            annual_cost_dollars=expense_cost,
            cost_type="explicit_fee",
            description="Fund expense ratios charged inside the holdings.",
        ),
        AnnualCostComponent(
            category="layered_fee",
            annual_rate=layered_cost / portfolio_value,
            annual_cost_dollars=layered_cost,
            cost_type="explicit_fee",
            description="Additional fund-of-funds or wrapper fee layering.",
        ),
        AnnualCostComponent(
            category="advisory_fee",
            annual_rate=advisory_cost / portfolio_value,
            annual_cost_dollars=advisory_cost,
            cost_type="explicit_fee",
            description="Portfolio-level or holding-specific advisory fee drag.",
        ),
    ]
    return components, per_holding

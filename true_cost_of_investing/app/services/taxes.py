from __future__ import annotations

from true_cost_of_investing.app.config import DEFAULT_ASSUMED_REALIZED_GAIN_RATIO
from true_cost_of_investing.app.models import AnnualCostComponent, NormalizedHolding, PortfolioAssumptions


def _combined_rate(primary: float, state: float) -> float:
    return max(primary + state, 0.0)


def calculate_tax_costs(
    holdings: list[NormalizedHolding],
    assumptions: PortfolioAssumptions,
    portfolio_value: float,
) -> tuple[list[AnnualCostComponent], list[dict[str, float]]]:
    per_holding: list[dict[str, float]] = []
    if assumptions.account_type in {"ira", "roth_ira", "401k"}:
        zero_components = [
            AnnualCostComponent("dividend_tax_drag", 0.0, 0.0, "tax_drag", "Dividend taxes are assumed deferred or avoided."),
            AnnualCostComponent("turnover_tax_drag", 0.0, 0.0, "tax_drag", "Turnover-related taxable gain realization is assumed deferred."),
            AnnualCostComponent("withholding_tax_drag", 0.0, 0.0, "tax_drag", "No withholding drag modeled in tax-advantaged accounts."),
        ]
        for holding in holdings:
            per_holding.append(
                {
                    "ticker": holding.ticker,
                    "dividend_tax_drag": 0.0,
                    "turnover_tax_drag": 0.0,
                    "withholding_tax_drag": 0.0,
                }
            )
        return zero_components, per_holding

    qualified_rate = _combined_rate(assumptions.qualified_dividend_tax_rate, assumptions.state_tax_rate)
    ordinary_rate = _combined_rate(assumptions.ordinary_income_tax_rate, assumptions.state_tax_rate)
    gains_rate = _combined_rate(assumptions.capital_gains_tax_rate, assumptions.state_tax_rate)

    dividend_tax = 0.0
    turnover_tax = 0.0
    withholding_tax = 0.0

    for holding in holdings:
        position_dividend_tax = holding.amount * (
            (holding.qualified_dividend_yield * qualified_rate)
            + (holding.nonqualified_dividend_yield * ordinary_rate)
        )
        position_turnover_tax = holding.amount * (
            holding.annual_turnover_rate * DEFAULT_ASSUMED_REALIZED_GAIN_RATIO * gains_rate
        )
        position_turnover_tax = max(position_turnover_tax - (holding.amount * assumptions.tax_loss_harvesting_benefit), 0.0)
        position_withholding_tax = holding.amount * holding.dividend_yield * holding.withholding_tax_rate

        dividend_tax += position_dividend_tax
        turnover_tax += position_turnover_tax
        withholding_tax += position_withholding_tax
        per_holding.append(
            {
                "ticker": holding.ticker,
                "dividend_tax_drag": round(position_dividend_tax, 2),
                "turnover_tax_drag": round(position_turnover_tax, 2),
                "withholding_tax_drag": round(position_withholding_tax, 2),
            }
        )

    components = [
        AnnualCostComponent(
            category="dividend_tax_drag",
            annual_rate=dividend_tax / portfolio_value,
            annual_cost_dollars=dividend_tax,
            cost_type="tax_drag",
            description="Taxes paid on qualified and non-qualified dividends in taxable accounts.",
        ),
        AnnualCostComponent(
            category="turnover_tax_drag",
            annual_rate=turnover_tax / portfolio_value,
            annual_cost_dollars=turnover_tax,
            cost_type="tax_drag",
            description="Estimated capital gains drag from turnover and realized appreciation.",
        ),
        AnnualCostComponent(
            category="withholding_tax_drag",
            annual_rate=withholding_tax / portfolio_value,
            annual_cost_dollars=withholding_tax,
            cost_type="tax_drag",
            description="Estimated foreign withholding tax drag on distributed income.",
        ),
    ]
    return components, per_holding

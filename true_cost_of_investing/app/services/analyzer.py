from __future__ import annotations

from typing import Any

from true_cost_of_investing.app.models import CostAnalysisResult, HoldingInput, PortfolioAssumptions
from true_cost_of_investing.app.services.comparison import compare_results
from true_cost_of_investing.app.services.fees import calculate_fee_costs
from true_cost_of_investing.app.services.insights import build_summary, generate_insights
from true_cost_of_investing.app.services.normalization import normalize_holdings
from true_cost_of_investing.app.services.projection import attribute_category_losses, build_projection
from true_cost_of_investing.app.services.recommendations import generate_recommendations
from true_cost_of_investing.app.services.taxes import calculate_tax_costs
from true_cost_of_investing.app.services.trading_costs import calculate_trading_costs


class TrueCostAnalyzer:
    def analyze(self, holdings: list[HoldingInput], assumptions: PortfolioAssumptions) -> CostAnalysisResult:
        normalized_holdings, blended_metrics = normalize_holdings(holdings)
        portfolio_value = blended_metrics["portfolio_value"]

        fee_components, fee_per_holding = calculate_fee_costs(normalized_holdings, assumptions, portfolio_value)
        tax_components, tax_per_holding = calculate_tax_costs(normalized_holdings, assumptions, portfolio_value)
        trading_components, trading_per_holding = calculate_trading_costs(normalized_holdings, assumptions, portfolio_value)

        cash_drag_component = {
            "category": "cash_drag",
            "annual_rate": assumptions.annual_cash_drag,
            "annual_cost_dollars": round(portfolio_value * assumptions.annual_cash_drag, 2),
            "cost_type": "implicit_friction",
            "description": "Estimated return shortfall from cash or low-yield idle capital.",
        }

        annual_breakdown = [component.__dict__ for component in fee_components + tax_components + trading_components]
        annual_breakdown.append(cash_drag_component)
        category_rates = {item["category"]: item["annual_rate"] for item in annual_breakdown}

        projection = build_projection(
            initial_value=portfolio_value,
            annual_gross_return=assumptions.annual_gross_return,
            assumptions=assumptions,
            category_rates=category_rates,
        )
        attributions = attribute_category_losses(
            initial_value=portfolio_value,
            annual_gross_return=assumptions.annual_gross_return,
            assumptions=assumptions,
            category_rates=category_rates,
            base_projection=projection,
        )

        per_holding_rows = []
        fee_map = {row["ticker"]: row for row in fee_per_holding}
        tax_map = {row["ticker"]: row for row in tax_per_holding}
        trading_map = {row["ticker"]: row for row in trading_per_holding}
        for holding in normalized_holdings:
            per_holding_rows.append(
                {
                    "ticker": holding.ticker,
                    "amount": round(holding.amount, 2),
                    "weight": round(holding.weight, 6),
                    "expense_ratio": holding.expense_ratio,
                    "annual_turnover_rate": holding.annual_turnover_rate,
                    **fee_map[holding.ticker],
                    **tax_map[holding.ticker],
                    **trading_map[holding.ticker],
                }
            )

        summary = build_summary(
            blended_metrics=blended_metrics,
            annual_breakdown=annual_breakdown,
            projected_ending_values=projection,
            dollars_lost_by_category=[item.__dict__ for item in attributions],
        )
        insights = generate_insights(summary, annual_breakdown, assumptions.__dict__)
        recommendations = generate_recommendations(
            holdings=per_holding_rows,
            assumptions=assumptions.__dict__,
            annual_breakdown=annual_breakdown,
        )
        horizon_table = [point.__dict__ for point in projection["timeline"] if point.year in {10, 20, 30, assumptions.investment_horizon_years}]
        horizon_table = sorted({row["year"]: row for row in horizon_table}.values(), key=lambda row: row["year"])

        chart_data = {
            "stacked_cost_breakdown": annual_breakdown,
            "loss_timeline": [point.__dict__ for point in projection["timeline"]],
            "gross_vs_net": [point.__dict__ for point in projection["timeline"]],
        }
        return CostAnalysisResult(
            normalized_holdings=[
                {
                    "ticker": row.ticker,
                    "amount": round(row.amount, 2),
                    "weight": round(row.weight, 6),
                    "expense_ratio": row.expense_ratio,
                    "dividend_yield": row.dividend_yield,
                    "annual_turnover_rate": row.annual_turnover_rate,
                    "estimated_spread_cost_bps": row.estimated_spread_cost_bps,
                    "withholding_tax_rate": row.withholding_tax_rate,
                    "layered_fee_ratio": row.layered_fee_ratio,
                }
                for row in normalized_holdings
            ],
            blended_cost_metrics={key: round(value, 6) if isinstance(value, float) else value for key, value in blended_metrics.items()},
            annual_friction_breakdown=[
                {key: round(value, 6) if isinstance(value, float) else value for key, value in row.items()}
                for row in annual_breakdown
            ],
            per_holding_cost_breakdown=per_holding_rows,
            projected_ending_values=projection,
            dollars_lost_by_category=[
                {
                    "category": row.category,
                    "direct_cost_dollars": round(row.direct_cost_dollars, 2),
                    "attributable_ending_value_loss": round(row.attributable_ending_value_loss, 2),
                    "attributable_percent_of_total_loss": round(row.attributable_percent_of_total_loss, 6),
                }
                for row in attributions
            ],
            timeline=[point.__dict__ for point in projection["timeline"]],
            comparison_table=horizon_table,
            summary=summary,
            insights=insights,
            recommendations=recommendations,
            chart_data=chart_data,
        )

    def compare(
        self,
        current_holdings: list[HoldingInput],
        alternative_holdings: list[HoldingInput],
        assumptions: PortfolioAssumptions,
    ):
        current = self.analyze(current_holdings, assumptions)
        alternative = self.analyze(alternative_holdings, assumptions)
        return compare_results(current, alternative)

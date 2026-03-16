from __future__ import annotations

from true_cost_of_investing.app.config import DEFAULT_REBALANCE_TRADE_FRACTION
from true_cost_of_investing.app.models import AnnualCostComponent, NormalizedHolding, PortfolioAssumptions


def calculate_trading_costs(
    holdings: list[NormalizedHolding],
    assumptions: PortfolioAssumptions,
    portfolio_value: float,
) -> tuple[list[AnnualCostComponent], list[dict[str, float]]]:
    per_holding: list[dict[str, float]] = []
    spread_drag = 0.0
    rebalance_drag = 0.0
    commissions = 0.0
    slippage_drag = 0.0

    for holding in holdings:
        spread_rate = holding.estimated_spread_cost_bps / 10000.0
        slippage_rate = assumptions.slippage_bps / 10000.0
        annual_trade_factor = max(holding.annual_turnover_rate, 0.05)
        position_spread = holding.amount * spread_rate * annual_trade_factor
        position_slippage = holding.amount * slippage_rate * annual_trade_factor
        position_rebalance = (
            holding.amount
            * (spread_rate + slippage_rate)
            * assumptions.rebalance_frequency_per_year
            * DEFAULT_REBALANCE_TRADE_FRACTION
        )
        estimated_trades = assumptions.rebalance_frequency_per_year + max(int(round(holding.annual_turnover_rate * 4)), 0)
        position_commissions = assumptions.commission_per_trade * estimated_trades

        spread_drag += position_spread
        slippage_drag += position_slippage
        rebalance_drag += position_rebalance
        commissions += position_commissions
        per_holding.append(
            {
                "ticker": holding.ticker,
                "spread_slippage_drag": round(position_spread + position_slippage, 2),
                "rebalance_drag": round(position_rebalance, 2),
                "commissions": round(position_commissions, 2),
            }
        )

    components = [
        AnnualCostComponent(
            category="spread_slippage_drag",
            annual_rate=(spread_drag + slippage_drag) / portfolio_value,
            annual_cost_dollars=spread_drag + slippage_drag,
            cost_type="implicit_friction",
            description="Estimated bid-ask spread and slippage costs from trading and turnover.",
        ),
        AnnualCostComponent(
            category="rebalance_drag",
            annual_rate=rebalance_drag / portfolio_value,
            annual_cost_dollars=rebalance_drag,
            cost_type="implicit_friction",
            description="Estimated friction from periodic rebalancing activity.",
        ),
        AnnualCostComponent(
            category="commissions",
            annual_rate=commissions / portfolio_value,
            annual_cost_dollars=commissions,
            cost_type="explicit_fee",
            description="Per-trade commission assumptions.",
        ),
    ]
    return components, per_holding

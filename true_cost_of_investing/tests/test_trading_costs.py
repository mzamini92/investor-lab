from true_cost_of_investing.app.models import HoldingInput, PortfolioAssumptions
from true_cost_of_investing.app.services.normalization import normalize_holdings
from true_cost_of_investing.app.services.trading_costs import calculate_trading_costs


def test_trading_cost_estimation() -> None:
    holdings = [
        HoldingInput("ARKK", 1000, 0.0075, "ETF", annual_turnover_rate=1.0, estimated_spread_cost_bps=10),
    ]
    normalized, metrics = normalize_holdings(holdings)
    assumptions = PortfolioAssumptions(
        monthly_contribution=0,
        annual_gross_return=0.08,
        investment_horizon_years=30,
        account_type="taxable",
        rebalance_frequency_per_year=2,
        commission_per_trade=5.0,
        slippage_bps=5.0,
    )
    components, _ = calculate_trading_costs(normalized, assumptions, metrics["portfolio_value"])
    component_map = {item.category: item.annual_cost_dollars for item in components}
    assert round(component_map["spread_slippage_drag"], 2) == 1.50
    assert round(component_map["rebalance_drag"], 2) == 0.30
    assert round(component_map["commissions"], 2) == 30.00

from true_cost_of_investing.app.models import HoldingInput, PortfolioAssumptions
from true_cost_of_investing.app.services.fees import calculate_fee_costs
from true_cost_of_investing.app.services.normalization import normalize_holdings


def test_fee_costs() -> None:
    holdings = [
        HoldingInput("VOO", 1000, 0.0010, "ETF", layered_fee_ratio=0.0005),
        HoldingInput("QQQ", 1000, 0.0020, "ETF"),
    ]
    normalized, metrics = normalize_holdings(holdings)
    assumptions = PortfolioAssumptions(0, 0.08, 30, "taxable", annual_advisory_fee=0.01)
    components, _ = calculate_fee_costs(normalized, assumptions, metrics["portfolio_value"])
    component_map = {item.category: item.annual_cost_dollars for item in components}
    assert round(component_map["expense_ratio"], 2) == 3.00
    assert round(component_map["layered_fee"], 2) == 0.50
    assert round(component_map["advisory_fee"], 2) == 20.00

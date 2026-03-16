from true_cost_of_investing.app.models import PortfolioAssumptions
from true_cost_of_investing.app.services.projection import build_projection


def test_projection_engine_reduces_net_value() -> None:
    assumptions = PortfolioAssumptions(
        monthly_contribution=100,
        annual_gross_return=0.08,
        investment_horizon_years=10,
        account_type="taxable",
    )
    projection = build_projection(
        initial_value=10000,
        annual_gross_return=0.08,
        assumptions=assumptions,
        category_rates={"expense_ratio": 0.001, "advisory_fee": 0.01},
    )
    assert projection["gross_ending_value"] > projection["net_ending_value"]
    assert projection["category_direct_costs"]["advisory_fee"] > projection["category_direct_costs"]["expense_ratio"]

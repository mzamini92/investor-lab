from true_cost_of_investing.app.models import HoldingInput, PortfolioAssumptions
from true_cost_of_investing.app.services.normalization import normalize_holdings
from true_cost_of_investing.app.services.taxes import calculate_tax_costs


def test_dividend_and_turnover_tax_drag() -> None:
    holdings = [
        HoldingInput(
            "SCHD",
            1000,
            0.0006,
            "ETF",
            dividend_yield=0.03,
            qualified_dividend_yield=0.02,
            nonqualified_dividend_yield=0.01,
            annual_turnover_rate=0.20,
            withholding_tax_rate=0.01,
        )
    ]
    normalized, metrics = normalize_holdings(holdings)
    assumptions = PortfolioAssumptions(
        monthly_contribution=0,
        annual_gross_return=0.08,
        investment_horizon_years=30,
        account_type="taxable",
        qualified_dividend_tax_rate=0.15,
        ordinary_income_tax_rate=0.24,
        capital_gains_tax_rate=0.15,
        state_tax_rate=0.05,
    )
    components, _ = calculate_tax_costs(normalized, assumptions, metrics["portfolio_value"])
    component_map = {item.category: item.annual_cost_dollars for item in components}
    assert round(component_map["dividend_tax_drag"], 2) == 6.90
    assert round(component_map["turnover_tax_drag"], 2) == 12.00
    assert round(component_map["withholding_tax_drag"], 2) == 0.30

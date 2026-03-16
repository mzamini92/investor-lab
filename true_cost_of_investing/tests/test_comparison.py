from true_cost_of_investing.app.models import HoldingInput, PortfolioAssumptions
from true_cost_of_investing.app.services.analyzer import TrueCostAnalyzer


def test_comparison_saves_money_for_lower_cost_portfolio() -> None:
    analyzer = TrueCostAnalyzer()
    assumptions = PortfolioAssumptions(300, 0.08, 30, "taxable", annual_advisory_fee=0.0075, state_tax_rate=0.05)
    current = [
        HoldingInput("QQQ", 10000, 0.0020, "ETF", qualified_dividend_yield=0.006, annual_turnover_rate=0.12),
        HoldingInput("ARKK", 5000, 0.0075, "ETF", annual_turnover_rate=0.85, estimated_spread_cost_bps=8),
    ]
    alternative = [
        HoldingInput("VTI", 10000, 0.0003, "ETF", qualified_dividend_yield=0.014, annual_turnover_rate=0.03),
        HoldingInput("VXUS", 5000, 0.0007, "ETF", qualified_dividend_yield=0.015, nonqualified_dividend_yield=0.01, annual_turnover_rate=0.08),
    ]
    result = analyzer.compare(current, alternative, assumptions)
    assert result.projected_savings["ending_value_savings"] > 0

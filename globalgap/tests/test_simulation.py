from globalgap.app.models import PortfolioPosition
from globalgap.app.portfolio import analyze_portfolio_exposure
from globalgap.app.simulation import run_diversification_simulation


def test_simulation_produces_two_portfolios() -> None:
    exposure = analyze_portfolio_exposure(
        [
            PortfolioPosition(ticker="VTI", quantity=100, price=100),
            PortfolioPosition(ticker="QQQ", quantity=10, price=100),
        ]
    )
    summary, adjustment, _ = run_diversification_simulation(exposure)
    assert summary.current_portfolio.label == "Current Portfolio"
    assert summary.diversified_portfolio.label == "Diversified Portfolio"
    assert adjustment.suggested_international_weight >= exposure.portfolio_international_weight

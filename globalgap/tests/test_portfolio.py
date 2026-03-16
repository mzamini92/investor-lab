from globalgap.app.models import PortfolioPosition
from globalgap.app.portfolio import analyze_portfolio_exposure


def test_portfolio_exposure_detects_us_bias() -> None:
    result = analyze_portfolio_exposure(
        [
            PortfolioPosition(ticker="VTI", quantity=100, price=100),
            PortfolioPosition(ticker="VXUS", quantity=10, price=100),
        ]
    )
    assert result.portfolio_us_weight > result.portfolio_international_weight
    assert result.home_bias_level in {"Severe US home bias", "High US home bias", "Moderate US home bias"}

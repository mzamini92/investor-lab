from global_etf_exposure_map.app.models import PortfolioPosition
from global_etf_exposure_map.app.utils.normalization import normalize_portfolio_weights


def test_portfolio_weight_normalization() -> None:
    weights = normalize_portfolio_weights(
        [
            PortfolioPosition("VTI", 200),
            PortfolioPosition("VXUS", 100),
            PortfolioPosition("QQQ", 100),
        ]
    )
    weight_map = {row["ticker"]: row["portfolio_weight"] for row in weights}
    assert weight_map["VTI"] == 0.5
    assert weight_map["VXUS"] == 0.25
    assert weight_map["QQQ"] == 0.25

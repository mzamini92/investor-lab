import math

from global_etf_exposure_map.app.models import ETFHoldings, HoldingRecord
from global_etf_exposure_map.app.providers.mock_provider import MockHoldingsProvider
from global_etf_exposure_map.app.services.analyzer import GlobalExposureAnalyzer


def build_provider() -> MockHoldingsProvider:
    return MockHoldingsProvider(
        {
            "ETF1": ETFHoldings(
                ticker="ETF1",
                label_region="North America",
                label_focus="US Total Market",
                holdings=[
                    HoldingRecord("ETF1", "AAA", "Alpha", 0.6, "Technology", "United States", "North America", "USD", "Mega Cap", 0.6, 0.1, 0.1, 0.1, 0.05, 0.05, "USA"),
                    HoldingRecord("ETF1", "BBB", "Beta", 0.4, "Healthcare", "United States", "North America", "USD", "Large Cap", 0.8, 0.1, 0.05, 0.0, 0.03, 0.02, "USA"),
                ],
            ),
            "ETF2": ETFHoldings(
                ticker="ETF2",
                label_region="Europe",
                label_focus="Europe Equity",
                holdings=[
                    HoldingRecord("ETF2", "AAA", "Alpha", 0.2, "Technology", "United States", "North America", "USD", "Mega Cap", 0.6, 0.1, 0.1, 0.1, 0.05, 0.05, "USA"),
                    HoldingRecord("ETF2", "CCC", "Gamma", 0.8, "Industrials", "Germany", "Europe", "EUR", "Large Cap", 0.2, 0.5, 0.1, 0.1, 0.05, 0.05, "DEU"),
                ],
            ),
        }
    )


def test_underlying_exposure_aggregation() -> None:
    analyzer = GlobalExposureAnalyzer(build_provider())
    result = analyzer.analyze([{"ticker": "ETF1", "amount": 50}, {"ticker": "ETF2", "amount": 50}])
    exposure_map = {row["underlying_ticker"]: row["exposure"] for row in result.underlying_company_exposures}
    assert math.isclose(exposure_map["AAA"], 0.4, rel_tol=1e-9)
    assert math.isclose(exposure_map["BBB"], 0.2, rel_tol=1e-9)
    assert math.isclose(exposure_map["CCC"], 0.4, rel_tol=1e-9)

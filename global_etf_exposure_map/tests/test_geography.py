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
                label_focus="US Core",
                holdings=[
                    HoldingRecord("ETF1", "AAA", "Alpha", 0.5, "Technology", "United States", "North America", "USD", "Mega Cap", 0.7, 0.1, 0.1, 0.05, 0.03, 0.02, "USA"),
                    HoldingRecord("ETF1", "BBB", "Beta", 0.5, "Financials", "Canada", "North America", "CAD", "Large Cap", 0.5, 0.2, 0.1, 0.05, 0.1, 0.05, "CAN"),
                ],
            ),
            "ETF2": ETFHoldings(
                ticker="ETF2",
                label_region="Asia Pacific",
                label_focus="Japan Equity",
                holdings=[
                    HoldingRecord("ETF2", "CCC", "Gamma", 1.0, "Industrials", "Japan", "Asia Pacific", "JPY", "Large Cap", 0.2, 0.2, 0.5, 0.05, 0.03, 0.02, "JPN"),
                ],
            ),
        }
    )


def test_country_and_region_aggregation() -> None:
    analyzer = GlobalExposureAnalyzer(build_provider())
    result = analyzer.analyze([{"ticker": "ETF1", "amount": 60}, {"ticker": "ETF2", "amount": 40}])

    country_map = {row["name"]: row["exposure"] for row in result.country_exposure_table}
    region_map = {row["name"]: row["exposure"] for row in result.region_exposure_table}
    assert math.isclose(country_map["United States"], 0.3, rel_tol=1e-9)
    assert math.isclose(country_map["Canada"], 0.3, rel_tol=1e-9)
    assert math.isclose(country_map["Japan"], 0.4, rel_tol=1e-9)
    assert math.isclose(region_map["North America"], 0.6, rel_tol=1e-9)
    assert math.isclose(region_map["Asia Pacific"], 0.4, rel_tol=1e-9)


def test_hhi_and_effective_country_count() -> None:
    analyzer = GlobalExposureAnalyzer(build_provider())
    result = analyzer.analyze([{"ticker": "ETF1", "amount": 60}, {"ticker": "ETF2", "amount": 40}])
    expected_hhi = (0.3**2) + (0.3**2) + (0.4**2)
    assert math.isclose(result.country_concentration_metrics["hhi"], expected_hhi, rel_tol=1e-6)
    assert math.isclose(result.country_concentration_metrics["effective_count"], 1 / expected_hhi, rel_tol=1e-6)

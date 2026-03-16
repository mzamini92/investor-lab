from global_etf_exposure_map.app.models import ETFHoldings, HoldingRecord
from global_etf_exposure_map.app.providers.mock_provider import MockHoldingsProvider
from global_etf_exposure_map.app.services.analyzer import GlobalExposureAnalyzer


def build_concentrated_provider() -> MockHoldingsProvider:
    return MockHoldingsProvider(
        {
            "US1": ETFHoldings(
                ticker="US1",
                label_region="North America",
                label_focus="US Growth",
                holdings=[
                    HoldingRecord("US1", "AAA", "Alpha", 1.0, "Technology", "United States", "North America", "USD", "Mega Cap", 0.8, 0.1, 0.05, 0.03, 0.01, 0.01, "USA"),
                ],
            )
        }
    )


def build_diversified_provider() -> MockHoldingsProvider:
    return MockHoldingsProvider(
        {
            "A": ETFHoldings(
                ticker="A",
                label_region="North America",
                label_focus="US Core",
                holdings=[
                    HoldingRecord("A", "AAA", "Alpha", 1.0, "Technology", "United States", "North America", "USD", "Mega Cap", 0.6, 0.1, 0.1, 0.1, 0.05, 0.05, "USA"),
                ],
            ),
            "B": ETFHoldings(
                ticker="B",
                label_region="Europe",
                label_focus="Europe",
                holdings=[
                    HoldingRecord("B", "BBB", "Beta", 1.0, "Industrials", "Germany", "Europe", "EUR", "Large Cap", 0.2, 0.5, 0.1, 0.1, 0.05, 0.05, "DEU"),
                ],
            ),
            "C": ETFHoldings(
                ticker="C",
                label_region="Asia Pacific",
                label_focus="Japan",
                holdings=[
                    HoldingRecord("C", "CCC", "Gamma", 1.0, "Consumer Discretionary", "Japan", "Asia Pacific", "JPY", "Large Cap", 0.15, 0.15, 0.5, 0.1, 0.05, 0.05, "JPN"),
                ],
            ),
        }
    )


def test_global_dependence_score_rewards_broader_exposure() -> None:
    concentrated = GlobalExposureAnalyzer(build_concentrated_provider()).analyze([{"ticker": "US1", "amount": 100}])
    diversified = GlobalExposureAnalyzer(build_diversified_provider()).analyze(
        [{"ticker": "A", "amount": 34}, {"ticker": "B", "amount": 33}, {"ticker": "C", "amount": 33}]
    )
    assert diversified.global_dependence_score > concentrated.global_dependence_score


def test_economic_reality_gap_is_non_negative() -> None:
    result = GlobalExposureAnalyzer(build_diversified_provider()).analyze(
        [{"ticker": "A", "amount": 50}, {"ticker": "B", "amount": 50}]
    )
    assert result.economic_reality_gap >= 0

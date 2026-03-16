from global_etf_exposure_map.app.models import ETFHoldings, HoldingRecord
from global_etf_exposure_map.app.providers.mock_provider import MockHoldingsProvider
from global_etf_exposure_map.app.services.analyzer import GlobalExposureAnalyzer


def build_provider() -> MockHoldingsProvider:
    return MockHoldingsProvider(
        {
            "US1": ETFHoldings(
                ticker="US1",
                label_region="North America",
                label_focus="US Growth",
                holdings=[
                    HoldingRecord("US1", "AAA", "Alpha", 1.0, "Technology", "United States", "North America", "USD", "Mega Cap", 0.85, 0.05, 0.03, 0.03, 0.02, 0.02, "USA"),
                ],
            ),
            "INTL": ETFHoldings(
                ticker="INTL",
                label_region="Europe",
                label_focus="Developed ex-US",
                holdings=[
                    HoldingRecord("INTL", "BBB", "Beta", 1.0, "Industrials", "United Kingdom", "Europe", "GBP", "Large Cap", 0.35, 0.4, 0.1, 0.1, 0.03, 0.02, "GBR"),
                ],
            ),
        }
    )


def test_warning_generation() -> None:
    result = GlobalExposureAnalyzer(build_provider()).analyze(
        [{"ticker": "US1", "amount": 80}, {"ticker": "INTL", "amount": 20}]
    )
    warning_blob = " ".join(result.warnings)
    assert "effectively exposed" in warning_blob or "Economic Reality Gap" in warning_blob

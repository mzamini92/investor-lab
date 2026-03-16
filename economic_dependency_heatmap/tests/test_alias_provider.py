from economic_dependency_heatmap.app.config import ETF_HOLDINGS_DIR
from economic_dependency_heatmap.app.providers.csv_provider import CSVDependencyDataProvider


def test_supported_dependency_aliases_are_exposed() -> None:
    provider = CSVDependencyDataProvider(ETF_HOLDINGS_DIR)
    supported = set(provider.supported_etfs())
    assert {
        "SPY",
        "IVV",
        "SPLG",
        "SCHX",
        "ITOT",
        "SCHB",
        "VEU",
        "ACWX",
        "VEA",
        "IEFA",
        "EFA",
        "SCHF",
        "IEMG",
        "VWO",
        "ONEQ",
        "QQQM",
    }.issubset(supported)


def test_dependency_alias_holdings_resolve() -> None:
    provider = CSVDependencyDataProvider(ETF_HOLDINGS_DIR)
    holdings = provider.get_holdings("SPY")
    assert holdings.ticker == "SPY"
    assert holdings.holdings

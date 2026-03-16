from hedgefund_dependency_engine.app.config import ETF_HOLDINGS_DIR
from hedgefund_dependency_engine.app.providers.csv_provider import CSVEngineDataProvider


def test_supported_engine_aliases_are_exposed() -> None:
    provider = CSVEngineDataProvider(ETF_HOLDINGS_DIR)
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


def test_engine_alias_holdings_resolve() -> None:
    provider = CSVEngineDataProvider(ETF_HOLDINGS_DIR)
    holdings = provider.get_holdings("SPY")
    assert holdings.ticker == "SPY"
    assert holdings.holdings

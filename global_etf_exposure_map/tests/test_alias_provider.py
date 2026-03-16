from global_etf_exposure_map.app.config import ETF_HOLDINGS_DIR
from global_etf_exposure_map.app.providers.csv_provider import CSVHoldingsProvider


def test_supported_global_aliases_are_exposed() -> None:
    provider = CSVHoldingsProvider(ETF_HOLDINGS_DIR)
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


def test_global_alias_holdings_resolve() -> None:
    provider = CSVHoldingsProvider(ETF_HOLDINGS_DIR)
    holdings = provider.get_holdings("SPY")
    assert holdings.ticker == "SPY"
    assert holdings.holdings

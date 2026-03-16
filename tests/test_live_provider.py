from __future__ import annotations

from etf_overlap.config import DEFAULT_DATA_DIR
from etf_overlap.providers.live_provider import LiveHybridHoldingsProvider


def test_live_hybrid_provider_supports_spy_via_local_proxy() -> None:
    provider = LiveHybridHoldingsProvider(DEFAULT_DATA_DIR)
    assert "SPY" in provider.supported_etfs()

    holdings = provider.get_holdings("SPY")
    assert holdings.ticker == "SPY"
    assert len(holdings.holdings) > 0


def test_live_hybrid_provider_supports_common_core_aliases() -> None:
    provider = LiveHybridHoldingsProvider(DEFAULT_DATA_DIR)
    supported = set(provider.supported_etfs())
    assert {
        "IVV",
        "SPLG",
        "ITOT",
        "SCHB",
        "VEU",
        "ACWX",
        "IEMG",
        "VWO",
        "ONEQ",
        "QQQM",
        "VEA",
        "IEFA",
        "EFA",
        "SCHF",
    }.issubset(supported)

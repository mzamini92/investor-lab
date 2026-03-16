from __future__ import annotations

from global_etf_exposure_map.app.exceptions import HoldingsNotFoundError
from global_etf_exposure_map.app.models import ETFHoldings
from global_etf_exposure_map.app.providers.base import HoldingsProvider


class MockHoldingsProvider(HoldingsProvider):
    def __init__(self, holdings_map: dict[str, ETFHoldings]) -> None:
        self._holdings_map = {ticker.upper(): holdings.normalized() for ticker, holdings in holdings_map.items()}

    def get_holdings(self, ticker: str) -> ETFHoldings:
        normalized_ticker = ticker.upper().strip()
        result = self._holdings_map.get(normalized_ticker)
        if result is None:
            raise HoldingsNotFoundError(f"Mock holdings not found for {normalized_ticker}")
        return result

    def supported_etfs(self) -> list[str]:
        return sorted(self._holdings_map)

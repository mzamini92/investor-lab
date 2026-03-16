from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from global_etf_exposure_map.app.models import ETFHoldings


class HoldingsProvider(ABC):
    """Abstract ETF holdings provider."""

    @abstractmethod
    def get_holdings(self, ticker: str) -> ETFHoldings:
        raise NotImplementedError

    def get_many(self, tickers: Iterable[str]) -> dict[str, ETFHoldings]:
        return {ticker.upper(): self.get_holdings(ticker) for ticker in tickers}

    @abstractmethod
    def supported_etfs(self) -> list[str]:
        raise NotImplementedError

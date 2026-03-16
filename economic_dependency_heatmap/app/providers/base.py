from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from economic_dependency_heatmap.app.models import ETFHoldings, MacroScenario


class DependencyDataProvider(ABC):
    """Abstract provider for enriched ETF holdings and scenario definitions."""

    @abstractmethod
    def get_holdings(self, ticker: str) -> ETFHoldings:
        raise NotImplementedError

    def get_many(self, tickers: Iterable[str]) -> dict[str, ETFHoldings]:
        return {ticker.upper(): self.get_holdings(ticker) for ticker in tickers}

    @abstractmethod
    def get_scenarios(self) -> list[MacroScenario]:
        raise NotImplementedError

    @abstractmethod
    def supported_etfs(self) -> list[str]:
        raise NotImplementedError

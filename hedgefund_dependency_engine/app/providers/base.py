from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from hedgefund_dependency_engine.app.models import ETFHoldings, EventTemplate, MacroScenario


class EngineDataProvider(ABC):
    @abstractmethod
    def get_holdings(self, ticker: str) -> ETFHoldings:
        raise NotImplementedError

    def get_many(self, tickers: Iterable[str]) -> dict[str, ETFHoldings]:
        return {ticker.upper(): self.get_holdings(ticker) for ticker in tickers}

    @abstractmethod
    def get_scenarios(self) -> list[MacroScenario]:
        raise NotImplementedError

    @abstractmethod
    def get_event_templates(self) -> list[EventTemplate]:
        raise NotImplementedError

    @abstractmethod
    def supported_etfs(self) -> list[str]:
        raise NotImplementedError

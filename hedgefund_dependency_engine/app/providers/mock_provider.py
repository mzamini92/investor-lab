from __future__ import annotations

from typing import Optional

from hedgefund_dependency_engine.app.exceptions import HoldingsNotFoundError
from hedgefund_dependency_engine.app.models import ETFHoldings, EventTemplate, MacroScenario
from hedgefund_dependency_engine.app.providers.base import EngineDataProvider


class MockEngineDataProvider(EngineDataProvider):
    def __init__(
        self,
        holdings_map: dict[str, ETFHoldings],
        scenarios: Optional[list[MacroScenario]] = None,
        event_templates: Optional[list[EventTemplate]] = None,
    ) -> None:
        self._holdings_map = {ticker.upper(): holdings.normalized() for ticker, holdings in holdings_map.items()}
        self._scenarios = list(scenarios or [])
        self._event_templates = list(event_templates or [])

    def get_holdings(self, ticker: str) -> ETFHoldings:
        normalized_ticker = ticker.upper().strip()
        result = self._holdings_map.get(normalized_ticker)
        if result is None:
            raise HoldingsNotFoundError(f"Mock holdings not found for {normalized_ticker}")
        return result

    def get_scenarios(self) -> list[MacroScenario]:
        return list(self._scenarios)

    def get_event_templates(self) -> list[EventTemplate]:
        return list(self._event_templates)

    def supported_etfs(self) -> list[str]:
        return sorted(self._holdings_map)

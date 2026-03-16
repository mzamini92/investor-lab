from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from value_check.app.models import ValuationSnapshot


class ValuationDataProvider(ABC):
    @abstractmethod
    def get_snapshot(self, ticker: str) -> ValuationSnapshot:
        raise NotImplementedError

    @abstractmethod
    def get_history(self, ticker: str) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def get_peers(self, ticker: str, peer_group: str | None = None) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def get_treasury_yield(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def supported_tickers(self) -> list[str]:
        raise NotImplementedError

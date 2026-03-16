from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from moat_watch.app.models import CommentaryRecord, QuarterlyMetrics


class MoatDataProvider(ABC):
    @abstractmethod
    def supported_tickers(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_company_quarter(self, ticker: str, quarter: str) -> QuarterlyMetrics:
        raise NotImplementedError

    @abstractmethod
    def get_company_history(self, ticker: str) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def get_peer_quarter_data(self, ticker: str, quarter: str) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def get_commentary(self, ticker: str, quarter: str) -> CommentaryRecord | None:
        raise NotImplementedError

    @abstractmethod
    def get_peer_group(self, ticker: str) -> list[str]:
        raise NotImplementedError

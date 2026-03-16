from __future__ import annotations

import pandas as pd

from value_check.app.models import ValuationSnapshot
from value_check.app.providers.base import ValuationDataProvider


class MockValuationProvider(ValuationDataProvider):
    def __init__(
        self,
        snapshots: dict[str, ValuationSnapshot],
        history: pd.DataFrame,
        peers: dict[str, pd.DataFrame],
        treasury_yield: float,
    ) -> None:
        self.snapshots = {ticker.upper(): snapshot for ticker, snapshot in snapshots.items()}
        self.history = history
        self.peers = {ticker.upper(): df for ticker, df in peers.items()}
        self.treasury_yield = treasury_yield

    def get_snapshot(self, ticker: str) -> ValuationSnapshot:
        return self.snapshots[ticker.upper()]

    def get_history(self, ticker: str) -> pd.DataFrame:
        return self.history.loc[self.history["ticker"].str.upper() == ticker.upper()].copy()

    def get_peers(self, ticker: str, peer_group: str | None = None) -> pd.DataFrame:
        return self.peers.get(ticker.upper(), pd.DataFrame()).copy()

    def get_treasury_yield(self) -> float:
        return self.treasury_yield

    def supported_tickers(self) -> list[str]:
        return sorted(self.snapshots)

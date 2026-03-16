from __future__ import annotations

import json

import pandas as pd

from value_check.app.config import CURRENT_SNAPSHOT_FILE, HISTORICAL_FILE, PEER_GROUP_FILE, TREASURY_RATE_FILE
from value_check.app.models import ValuationSnapshot
from value_check.app.providers.base import ValuationDataProvider
from value_check.app.services.ratios import calculate_current_metrics


class LocalValuationProvider(ValuationDataProvider):
    def __init__(self) -> None:
        self._snapshots = {
            item["ticker"].upper(): item
            for item in json.loads(CURRENT_SNAPSHOT_FILE.read_text(encoding="utf-8"))
        }
        self._history = pd.read_csv(HISTORICAL_FILE)
        self._peer_groups = json.loads(PEER_GROUP_FILE.read_text(encoding="utf-8"))
        self._treasury = json.loads(TREASURY_RATE_FILE.read_text(encoding="utf-8"))

    def get_snapshot(self, ticker: str) -> ValuationSnapshot:
        payload = self._snapshots.get(ticker.upper())
        if payload is None:
            raise ValueError(f"Ticker not supported: {ticker}")
        return ValuationSnapshot(**payload)

    def get_history(self, ticker: str) -> pd.DataFrame:
        return self._history.loc[self._history["ticker"].str.upper() == ticker.upper()].copy()

    def get_peers(self, ticker: str, peer_group: str | None = None) -> pd.DataFrame:
        snapshot = self.get_snapshot(ticker)
        group_name = peer_group or snapshot.peer_group or ticker.upper()
        peer_tickers = self._peer_groups.get(group_name, [])
        rows = []
        for item in peer_tickers:
            if item not in self._snapshots or item == ticker.upper():
                continue
            peer_snapshot = ValuationSnapshot(**self._snapshots[item])
            peer_metrics, _ = calculate_current_metrics(
                peer_snapshot,
                peer_snapshot.current_treasury_yield or self.get_treasury_yield(),
            )
            rows.append(
                {
                    **self._snapshots[item],
                    **peer_metrics,
                }
            )
        return pd.DataFrame(rows)

    def get_treasury_yield(self) -> float:
        return float(self._treasury["ten_year_treasury_yield"])

    def supported_tickers(self) -> list[str]:
        return sorted(self._snapshots)

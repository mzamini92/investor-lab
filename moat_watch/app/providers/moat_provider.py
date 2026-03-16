from __future__ import annotations

import json

import pandas as pd

from moat_watch.app.config import COMMENTARY_FILE, COMPANIES_FILE, PEER_GROUPS_FILE
from moat_watch.app.models import CommentaryRecord, QuarterlyMetrics
from moat_watch.app.providers.base import MoatDataProvider


class LocalMoatProvider(MoatDataProvider):
    def __init__(self) -> None:
        self._metrics = pd.read_csv(COMPANIES_FILE)
        self._peer_groups = json.loads(PEER_GROUPS_FILE.read_text(encoding="utf-8"))
        self._commentary_rows = {
            (str(item["ticker"]).upper(), str(item["quarter"]).upper()): item
            for item in json.loads(COMMENTARY_FILE.read_text(encoding="utf-8"))
        }

    def supported_tickers(self) -> list[str]:
        tracked = sorted(
            ticker
            for ticker in self._metrics["ticker"].str.upper().unique().tolist()
            if ticker in self._peer_groups
        )
        return tracked

    def get_company_quarter(self, ticker: str, quarter: str) -> QuarterlyMetrics:
        rows = self._metrics.loc[
            (self._metrics["ticker"].str.upper() == ticker.upper())
            & (self._metrics["quarter_label"].str.upper() == quarter.upper())
        ]
        if rows.empty:
            raise ValueError(f"No quarterly metrics found for {ticker} {quarter}.")
        payload = rows.iloc[0].replace({pd.NA: None}).to_dict()
        return QuarterlyMetrics(**{k: (None if pd.isna(v) else v) for k, v in payload.items() if k != "quarter_label"})

    def get_company_history(self, ticker: str) -> pd.DataFrame:
        history = self._metrics.loc[self._metrics["ticker"].str.upper() == ticker.upper()].copy()
        history["quarter_sort"] = history["fiscal_year"] * 10 + history["fiscal_quarter"]
        return history.sort_values("quarter_sort").reset_index(drop=True)

    def get_peer_quarter_data(self, ticker: str, quarter: str) -> pd.DataFrame:
        peers = self.get_peer_group(ticker)
        if not peers:
            return pd.DataFrame()
        rows = self._metrics.loc[
            self._metrics["ticker"].str.upper().isin(peers)
            & (self._metrics["quarter_label"].str.upper() == quarter.upper())
        ].copy()
        return rows.reset_index(drop=True)

    def get_commentary(self, ticker: str, quarter: str) -> CommentaryRecord | None:
        payload = self._commentary_rows.get((ticker.upper(), quarter.upper()))
        return CommentaryRecord(**payload) if payload else None

    def get_peer_group(self, ticker: str) -> list[str]:
        return list(self._peer_groups.get(ticker.upper(), []))

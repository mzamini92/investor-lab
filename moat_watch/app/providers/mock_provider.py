from __future__ import annotations

import pandas as pd

from moat_watch.app.models import CommentaryRecord, QuarterlyMetrics
from moat_watch.app.providers.base import MoatDataProvider


class MockMoatProvider(MoatDataProvider):
    def __init__(
        self,
        metrics: list[QuarterlyMetrics],
        peer_groups: dict[str, list[str]],
        commentary: list[CommentaryRecord] | None = None,
    ) -> None:
        self._metrics_df = pd.DataFrame([metric.__dict__ | {"quarter_label": metric.quarter_label} for metric in metrics])
        self._peer_groups = {key.upper(): [item.upper() for item in value] for key, value in peer_groups.items()}
        self._commentary = {(item.ticker.upper(), item.quarter.upper()): item for item in (commentary or [])}

    def supported_tickers(self) -> list[str]:
        return sorted(self._peer_groups)

    def get_company_quarter(self, ticker: str, quarter: str) -> QuarterlyMetrics:
        rows = self._metrics_df.loc[
            (self._metrics_df["ticker"].str.upper() == ticker.upper())
            & (self._metrics_df["quarter_label"].str.upper() == quarter.upper())
        ]
        if rows.empty:
            raise ValueError(f"Missing quarter: {ticker} {quarter}")
        payload = rows.iloc[0].to_dict()
        payload.pop("quarter_label", None)
        return QuarterlyMetrics(**payload)

    def get_company_history(self, ticker: str) -> pd.DataFrame:
        rows = self._metrics_df.loc[self._metrics_df["ticker"].str.upper() == ticker.upper()].copy()
        rows["quarter_sort"] = rows["fiscal_year"] * 10 + rows["fiscal_quarter"]
        return rows.sort_values("quarter_sort").reset_index(drop=True)

    def get_peer_quarter_data(self, ticker: str, quarter: str) -> pd.DataFrame:
        return self._metrics_df.loc[
            self._metrics_df["ticker"].str.upper().isin(self.get_peer_group(ticker))
            & (self._metrics_df["quarter_label"].str.upper() == quarter.upper())
        ].copy()

    def get_commentary(self, ticker: str, quarter: str) -> CommentaryRecord | None:
        return self._commentary.get((ticker.upper(), quarter.upper()))

    def get_peer_group(self, ticker: str) -> list[str]:
        return list(self._peer_groups.get(ticker.upper(), []))

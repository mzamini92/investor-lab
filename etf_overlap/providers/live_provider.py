from __future__ import annotations

from abc import ABC, abstractmethod
from io import StringIO
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

from etf_overlap.exceptions import HoldingsNotFoundError
from etf_overlap.models import ETFHoldings, HoldingRecord
from etf_overlap.providers.base import HoldingsProvider
from etf_overlap.providers.csv_provider import CSVHoldingsProvider


class RemoteHoldingsFetcher(ABC):
    """Interface for live, on-demand ETF holdings fetchers."""

    @abstractmethod
    def can_handle(self, ticker: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def fetch(self, ticker: str) -> ETFHoldings:
        raise NotImplementedError

    def advertised_tickers(self) -> list[str]:
        return []


class SPDRHtmlHoldingsFetcher(RemoteHoldingsFetcher):
    """Best-effort official SPDR holdings fetcher using fund holdings tables on ssga.com."""

    URL_MAP = {
        "SPY": "https://www.ssga.com/us/en/intermediary/etfs/spdr-sp-500-etf-trust-spy",
        "SPDW": "https://www.ssga.com/us/en/intermediary/etfs/spdr-portfolio-developed-world-ex-us-etf-spdw",
    }

    def __init__(self, metadata_map: dict[str, dict[str, object]], session: Optional[requests.Session] = None) -> None:
        self.metadata_map = metadata_map
        self.session = session or requests.Session()

    def can_handle(self, ticker: str) -> bool:
        return ticker.upper().strip() in self.URL_MAP

    def advertised_tickers(self) -> list[str]:
        return sorted(self.URL_MAP)

    def fetch(self, ticker: str) -> ETFHoldings:
        normalized = ticker.upper().strip()
        if normalized not in self.URL_MAP:
            raise HoldingsNotFoundError(f"No live SPDR holdings source configured for {normalized}.")

        response = self.session.get(self.URL_MAP[normalized], timeout=20)
        response.raise_for_status()
        tables = pd.read_html(StringIO(response.text))

        holdings_table = None
        for table in tables:
            columns = {str(col).strip().lower() for col in table.columns}
            if "name" in columns and "weight" in columns:
                holdings_table = table
                break
        if holdings_table is None:
            raise HoldingsNotFoundError(f"Unable to parse live SPDR holdings table for {normalized}.")

        records: list[HoldingRecord] = []
        for row in holdings_table.itertuples(index=False):
            row_map = dict(zip(holdings_table.columns, row))
            name = str(row_map.get("Name", row_map.get("NAME", ""))).strip()
            weight_raw = str(row_map.get("Weight", row_map.get("WEIGHT", ""))).strip().replace("%", "")
            if not name or not weight_raw:
                continue
            try:
                weight = float(weight_raw) / 100.0
            except ValueError:
                continue
            stock_ticker = self._infer_ticker_from_name(name)
            metadata = self.metadata_map.get(stock_ticker, {})
            records.append(
                HoldingRecord(
                    stock_ticker=stock_ticker,
                    company_name=name,
                    weight=weight,
                    sector=str(metadata.get("sector", "Unknown")),
                    country=str(metadata.get("country", "Unknown")),
                    market_cap=float(metadata["market_cap"]) if metadata.get("market_cap") is not None else None,
                    style_box=str(metadata.get("style_box", "Unknown")),
                )
            )

        if not records:
            raise HoldingsNotFoundError(f"Live SPDR fetch returned no usable holdings for {normalized}.")
        return ETFHoldings(ticker=normalized, holdings=records).normalized()

    @staticmethod
    def _infer_ticker_from_name(name: str) -> str:
        base = (
            name.replace("Class A", "")
            .replace("CLASS A", "")
            .replace("Class C", "")
            .replace("CLASS C", "")
            .replace("Inc.", "")
            .replace("Corporation", "")
            .replace("Corp.", "")
            .replace(".", "")
            .strip()
        )
        alias_map = {
            "APPLE INC": "AAPL",
            "MICROSOFT CORP": "MSFT",
            "MICROSOFT": "MSFT",
            "NVIDIA CORP": "NVDA",
            "AMAZONCOM INC": "AMZN",
            "AMAZONCOM": "AMZN",
            "ALPHABET INC CL A": "GOOGL",
            "ALPHABET INC CL C": "GOOG",
            "META PLATFORMS INC": "META",
            "META PLATFORMS INC CLASS A": "META",
            "TESLA INC": "TSLA",
            "BERKSHIRE HATHAWAY INC CL B": "BRK.B",
            "BROADCOM INC": "AVGO",
            "ELI LILLY AND COMPANY": "LLY",
            "JPMORGAN CHASE + CO": "JPM",
            "JPMORGAN CHASE & CO": "JPM",
            "EXXON MOBIL CORP": "XOM",
        }
        upper = base.upper()
        return alias_map.get(upper, upper.replace(" ", "")[:10])


class LiveHybridHoldingsProvider(HoldingsProvider):
    """Hybrid provider: local CSV first, then best-effort live fetch, cached in memory."""

    PROXY_ALIAS_MAP = {
        "VEA": "SPDW",
        "IEFA": "SPDW",
        "EFA": "SPDW",
        "SCHF": "SPDW",
    }

    def __init__(
        self,
        data_dir: str | Path,
        *,
        local_provider: Optional[CSVHoldingsProvider] = None,
        remote_fetchers: Optional[list[RemoteHoldingsFetcher]] = None,
    ) -> None:
        self.local_provider = local_provider or CSVHoldingsProvider(data_dir)
        self._metadata_map = self._build_metadata_map(Path(data_dir))
        self.remote_fetchers = remote_fetchers or [SPDRHtmlHoldingsFetcher(self._metadata_map)]
        self._cache: dict[str, ETFHoldings] = {}

    def get_holdings(self, ticker: str) -> ETFHoldings:
        normalized = ticker.upper().strip()
        if normalized in self._cache:
            return self._cache[normalized]

        try:
            holdings = self.local_provider.get_holdings(normalized)
        except HoldingsNotFoundError:
            proxy_target = self.PROXY_ALIAS_MAP.get(normalized)
            if proxy_target:
                proxied = self.get_holdings(proxy_target)
                holdings = ETFHoldings(ticker=normalized, holdings=proxied.holdings).normalized()
            else:
                holdings = self._fetch_live(normalized)

        self._cache[normalized] = holdings
        return holdings

    def supported_etfs(self) -> list[str]:
        supported = set(self.local_provider.supported_etfs())
        advertised: set[str] = set()
        for fetcher in self.remote_fetchers:
            advertised.update(fetcher.advertised_tickers())
        supported.update(advertised)
        for alias, target in self.PROXY_ALIAS_MAP.items():
            if target in supported or target in advertised:
                supported.add(alias)
        return sorted(supported)

    def _fetch_live(self, ticker: str) -> ETFHoldings:
        for fetcher in self.remote_fetchers:
            if not fetcher.can_handle(ticker):
                continue
            try:
                return fetcher.fetch(ticker)
            except Exception as exc:  # noqa: BLE001
                raise HoldingsNotFoundError(f"Unable to fetch live holdings for {ticker}: {exc}") from exc
        raise HoldingsNotFoundError(f"No local or live holdings source is available for ETF {ticker}.")

    @staticmethod
    def _build_metadata_map(data_dir: Path) -> dict[str, dict[str, object]]:
        metadata: dict[str, dict[str, object]] = {}
        for csv_path in data_dir.glob("*.csv"):
            try:
                df = pd.read_csv(csv_path)
            except Exception:  # noqa: BLE001
                continue
            for row in df.to_dict(orient="records"):
                stock_ticker = str(row.get("stock_ticker", "")).upper().strip()
                if not stock_ticker or stock_ticker in metadata:
                    continue
                metadata[stock_ticker] = {
                    "sector": row.get("sector") or "Unknown",
                    "country": row.get("country") or "Unknown",
                    "market_cap": row.get("market_cap"),
                    "style_box": row.get("style_box") or "Unknown",
                }
        return metadata

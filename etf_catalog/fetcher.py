from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import Optional, Union

import pandas as pd
import requests


NASDAQ_TRADED_URL = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqtraded.txt"
OTHER_LISTED_URL = "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"


def _parse_pipe_delimited_text(raw_text: str) -> pd.DataFrame:
    cleaned_lines = [line for line in raw_text.splitlines() if line.strip()]
    if cleaned_lines and cleaned_lines[-1].startswith("File Creation Time"):
        cleaned_lines = cleaned_lines[:-1]
    return pd.read_csv(StringIO("\n".join(cleaned_lines)), sep="|")


def parse_nasdaq_traded_text(raw_text: str) -> pd.DataFrame:
    df = _parse_pipe_delimited_text(raw_text)
    df = df.rename(
        columns={
            "Symbol": "ticker",
            "Security Name": "security_name",
            "Listing Exchange": "listing_exchange",
            "ETF": "is_etf",
        }
    )
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["security_name"] = df["security_name"].astype(str).str.strip()
    df["listing_exchange"] = df["listing_exchange"].astype(str).str.strip()
    df["is_etf"] = df["is_etf"].astype(str).str.upper().str.strip()
    return df[["ticker", "security_name", "listing_exchange", "is_etf"]]


def parse_other_listed_text(raw_text: str) -> pd.DataFrame:
    df = _parse_pipe_delimited_text(raw_text)
    df = df.rename(
        columns={
            "ACT Symbol": "ticker",
            "Security Name": "security_name",
            "Exchange": "listing_exchange",
            "ETF": "is_etf",
        }
    )
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["security_name"] = df["security_name"].astype(str).str.strip()
    df["listing_exchange"] = df["listing_exchange"].astype(str).str.strip()
    df["is_etf"] = df["is_etf"].astype(str).str.upper().str.strip()
    return df[["ticker", "security_name", "listing_exchange", "is_etf"]]


def fetch_all_us_etfs(session: Optional[requests.Session] = None) -> pd.DataFrame:
    http = session or requests.Session()
    nasdaq_response = http.get(NASDAQ_TRADED_URL, timeout=30)
    nasdaq_response.raise_for_status()
    other_response = http.get(OTHER_LISTED_URL, timeout=30)
    other_response.raise_for_status()

    frames = [
        parse_nasdaq_traded_text(nasdaq_response.text),
        parse_other_listed_text(other_response.text),
    ]
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.loc[combined["is_etf"] == "Y"].copy()
    combined["source"] = "nasdaq_trader"
    combined = combined.drop_duplicates(subset=["ticker"]).sort_values("ticker").reset_index(drop=True)
    return combined[["ticker", "security_name", "listing_exchange", "source"]]


def save_etf_catalog(output_path: Union[str, Path], session: Optional[requests.Session] = None) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    catalog_df = fetch_all_us_etfs(session=session)
    catalog_df.to_csv(path, index=False)
    return path


def load_etf_catalog(path: Union[str, Path]) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        return pd.DataFrame(columns=["ticker", "security_name", "listing_exchange", "source"])
    return pd.read_csv(csv_path)

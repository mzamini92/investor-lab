from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class MetadataRecord:
    country_name: str
    country_code: str
    region: str
    currency: str


@dataclass
class ImportSummary:
    etf_ticker: str
    holdings_count: int
    overlap_path: Optional[str]
    global_path: Optional[str]


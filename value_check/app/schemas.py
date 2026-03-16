from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ValueCheckRequest(BaseModel):
    ticker: str = Field(..., min_length=1)
    asset_type: str = "auto"
    sector_override: Optional[str] = None
    treasury_yield: Optional[float] = None
    lookback_years: int = 10
    peer_group: Optional[str] = None


from __future__ import annotations

from pydantic import BaseModel, Field, PositiveFloat


class PortfolioPositionRequest(BaseModel):
    ticker: str = Field(..., min_length=1)
    amount: PositiveFloat


class AnalyzeGlobalExposureRequest(BaseModel):
    positions: list[PortfolioPositionRequest]


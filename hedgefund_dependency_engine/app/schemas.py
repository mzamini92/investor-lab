from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, PositiveFloat, field_validator


class PortfolioPositionRequest(BaseModel):
    ticker: str = Field(..., min_length=1)
    amount: PositiveFloat


class DynamicEventRequest(BaseModel):
    name: str = Field(..., min_length=1)
    severity: float = Field(default=1.0, gt=0.0, le=3.0)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()


class AnalyzePortfolioRequest(BaseModel):
    positions: list[PortfolioPositionRequest]
    scenario_names: Optional[list[str]] = None
    dynamic_events: Optional[list[DynamicEventRequest]] = None
    headline_context: Optional[str] = None

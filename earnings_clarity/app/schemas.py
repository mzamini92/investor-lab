from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, PositiveFloat


class HoldingPositionRequest(BaseModel):
    ticker: str = Field(..., min_length=1)
    shares: PositiveFloat


class EarningsEventRequest(BaseModel):
    ticker: str
    company_name: str
    quarter: str
    earnings_date: str
    revenue_actual: float
    revenue_estimate: float
    eps_actual: float
    eps_estimate: float
    guidance_summary: str = ""


class TranscriptUtteranceRequest(BaseModel):
    speaker: str
    speaker_role: str = "unknown"
    section: str = "unknown"
    text: str
    order: int = 0


class TranscriptPayloadRequest(BaseModel):
    ticker: str
    quarter: str
    raw_text: Optional[str] = None
    utterances: Optional[list[TranscriptUtteranceRequest]] = None


class AnalyzeEarningsCallRequest(BaseModel):
    earnings_event: EarningsEventRequest
    transcript: TranscriptPayloadRequest
    prior_transcript: Optional[TranscriptPayloadRequest] = None


class AnalyzePortfolioQuarterRequest(BaseModel):
    holdings: list[HoldingPositionRequest]
    quarter: str

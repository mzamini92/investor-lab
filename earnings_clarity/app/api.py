from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException

from earnings_clarity.app.config import DEFAULT_SAMPLE_HOLDINGS, DEFAULT_SAMPLE_QUARTER, EARNINGS_DIR, HOLDINGS_DIR
from earnings_clarity.app.exceptions import EarningsClarityError
from earnings_clarity.app.models import EarningsEvent, Transcript, TranscriptUtterance
from earnings_clarity.app.schemas import AnalyzeEarningsCallRequest, AnalyzePortfolioQuarterRequest
from earnings_clarity.app.services.analyzer import EarningsClarityAnalyzer
from earnings_clarity.app.services.parser import parse_raw_transcript
from earnings_clarity.app.services.portfolio import analyze_portfolio_quarter
from earnings_clarity.app.utils.validation import validate_holdings


def _request_transcript_to_model(payload) -> Transcript:
    if payload.raw_text:
        return parse_raw_transcript(ticker=payload.ticker, quarter=payload.quarter, raw_text=payload.raw_text)
    utterances = [
        TranscriptUtterance(
            speaker=item.speaker,
            speaker_role=item.speaker_role,  # type: ignore[arg-type]
            section=item.section,  # type: ignore[arg-type]
            text=item.text,
            order=item.order,
        )
        for item in payload.utterances or []
    ]
    return Transcript(ticker=payload.ticker, quarter=payload.quarter, utterances=utterances, source="request")


def create_app() -> FastAPI:
    app = FastAPI(
        title="EarningsClarity",
        version="0.1.0",
        description="Plain-English earnings call clarity for long-term investors.",
    )
    analyzer = EarningsClarityAnalyzer()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/sample-holdings")
    async def sample_holdings() -> list[dict[str, Any]]:
        return DEFAULT_SAMPLE_HOLDINGS

    @app.get("/sample-companies")
    async def sample_companies() -> list[dict[str, str]]:
        return [{"ticker": path.stem.split("_")[0], "quarter": path.stem.split("_")[1]} for path in sorted(EARNINGS_DIR.glob("*.json"))]

    @app.get("/sample-earnings-events")
    async def sample_earnings_events() -> list[dict[str, Any]]:
        return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(EARNINGS_DIR.glob("*.json"))]

    @app.get("/sample-summary/{ticker}")
    async def sample_summary(ticker: str) -> dict[str, Any]:
        prior_quarter = "2025Q3"
        return analyzer.analyze_saved_call(ticker.upper(), DEFAULT_SAMPLE_QUARTER, prior_quarter=prior_quarter).to_dict()

    @app.post("/analyze-earnings-call")
    async def analyze_earnings_call(request: AnalyzeEarningsCallRequest) -> dict[str, Any]:
        try:
            event = EarningsEvent(**request.earnings_event.model_dump())
            transcript = _request_transcript_to_model(request.transcript)
            prior = None if request.prior_transcript is None else _request_transcript_to_model(request.prior_transcript)
            result = analyzer.analyze_call(earnings_event=event, transcript=transcript, prior_transcript=prior)
        except EarningsClarityError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result.to_dict()

    @app.post("/analyze-portfolio-quarter")
    async def analyze_portfolio(request: AnalyzePortfolioQuarterRequest) -> dict[str, Any]:
        try:
            holdings = validate_holdings([item.model_dump() for item in request.holdings])
            results = analyze_portfolio_quarter(analyzer, holdings, request.quarter)
        except EarningsClarityError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"quarter": request.quarter, "results": results}

    return app


app = create_app()

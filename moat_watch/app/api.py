from __future__ import annotations

import json
from typing import Any

from fastapi import FastAPI, HTTPException

from moat_watch.app.config import DEFAULT_QUARTER, DEFAULT_WATCHLIST, WATCHLIST_FILE
from moat_watch.app.models import CommentaryRecord, QuarterlyMetrics, WatchlistItem
from moat_watch.app.providers.moat_provider import LocalMoatProvider
from moat_watch.app.schemas import AnalyzeCompanyMoatRequest, AnalyzeWatchlistQuarterRequest
from moat_watch.app.services.analyzer import MoatWatchAnalyzer


def create_app() -> FastAPI:
    app = FastAPI(title="MoatWatch", version="0.1.0", description="Quarterly moat-health monitoring for long-term investors.")
    analyzer = MoatWatchAnalyzer()
    provider = LocalMoatProvider()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/sample-watchlist")
    async def sample_watchlist() -> list[dict[str, Any]]:
        return json.loads(WATCHLIST_FILE.read_text(encoding="utf-8"))

    @app.get("/sample-companies")
    async def sample_companies() -> list[str]:
        return provider.supported_tickers()

    @app.get("/sample-result/{ticker}")
    async def sample_result(ticker: str) -> dict[str, Any]:
        return analyzer.analyze(ticker, DEFAULT_QUARTER).to_dict()

    @app.get("/peer-comparison/{ticker}")
    async def peer_comparison(ticker: str, quarter: str = DEFAULT_QUARTER) -> list[dict[str, Any]]:
        return analyzer.analyze(ticker, quarter).peer_comparison

    @app.post("/analyze-company-moat")
    async def analyze_company_moat(request: AnalyzeCompanyMoatRequest) -> dict[str, Any]:
        try:
            if request.current_metrics is not None:
                result = analyzer.analyze_from_inputs(
                    QuarterlyMetrics(**request.current_metrics.model_dump()),
                    prior_quarter=QuarterlyMetrics(**request.prior_quarter.model_dump()) if request.prior_quarter else None,
                    prior_year_quarter=QuarterlyMetrics(**request.prior_year_quarter.model_dump()) if request.prior_year_quarter else None,
                    peer_metrics=[QuarterlyMetrics(**item.model_dump()) for item in (request.peer_data or [])],
                    commentary=CommentaryRecord(**request.commentary.model_dump()) if request.commentary else None,
                )
            else:
                if not request.ticker:
                    raise ValueError("ticker is required when current_metrics is not provided.")
                result = analyzer.analyze(request.ticker, request.quarter or DEFAULT_QUARTER)
            return result.to_dict()
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/analyze-watchlist-quarter")
    async def analyze_watchlist_quarter(request: AnalyzeWatchlistQuarterRequest) -> dict[str, Any]:
        try:
            result = analyzer.analyze_watchlist(
                [WatchlistItem(**item.model_dump()) for item in request.watchlist],
                request.quarter,
            )
            return result.to_dict()
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app()

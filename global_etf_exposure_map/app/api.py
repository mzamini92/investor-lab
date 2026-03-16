from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException

from global_etf_exposure_map.app.config import DEFAULT_SAMPLE_PORTFOLIO
from global_etf_exposure_map.app.exceptions import GlobalExposureError
from global_etf_exposure_map.app.schemas import AnalyzeGlobalExposureRequest
from global_etf_exposure_map.app.services.analyzer import GlobalExposureAnalyzer


def create_app() -> FastAPI:
    app = FastAPI(
        title="Global ETF Exposure Map",
        version="0.1.0",
        description="Analyze the true geographic and economic exposure of ETF portfolios.",
    )
    analyzer = GlobalExposureAnalyzer()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/sample-portfolio")
    async def sample_portfolio() -> list[dict[str, Any]]:
        return DEFAULT_SAMPLE_PORTFOLIO

    @app.get("/supported-etfs")
    async def supported_etfs() -> dict[str, list[str]]:
        return {"tickers": analyzer.holdings_provider.supported_etfs()}

    @app.get("/sample-map-data")
    async def sample_map_data() -> list[dict[str, Any]]:
        return analyzer.analyze(DEFAULT_SAMPLE_PORTFOLIO).map_ready_data

    @app.post("/analyze-global-exposure")
    async def analyze_global_exposure(request: AnalyzeGlobalExposureRequest) -> dict[str, Any]:
        try:
            result = analyzer.analyze([position.model_dump() for position in request.positions])
        except GlobalExposureError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result.to_dict()

    return app


app = create_app()

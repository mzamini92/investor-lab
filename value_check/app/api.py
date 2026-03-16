from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException

from value_check.app.config import DEFAULT_SAMPLE_TICKERS
from value_check.app.schemas import ValueCheckRequest
from value_check.app.services.analyzer import ValueCheckAnalyzer


def create_app() -> FastAPI:
    app = FastAPI(
        title="ValueCheck",
        version="0.1.0",
        description="Show valuation context versus history and peers with a plain-English verdict.",
    )
    analyzer = ValueCheckAnalyzer()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/supported-tickers")
    async def supported_tickers() -> list[str]:
        return analyzer.provider.supported_tickers()

    @app.get("/sample-tickers")
    async def sample_tickers() -> list[str]:
        return DEFAULT_SAMPLE_TICKERS

    @app.get("/sample-result/{ticker}")
    async def sample_result(ticker: str) -> dict[str, Any]:
        return analyzer.analyze(ticker).to_dict()

    @app.get("/peer-group/{ticker}")
    async def peer_group(ticker: str) -> list[dict[str, Any]]:
        df = analyzer.provider.get_peers(ticker)
        return df.to_dict(orient="records")

    @app.post("/value-check")
    async def value_check(request: ValueCheckRequest) -> dict[str, Any]:
        try:
            return analyzer.analyze(
                request.ticker,
                lookback_years=request.lookback_years,
                treasury_yield=request.treasury_yield,
                peer_group=request.peer_group,
            ).to_dict()
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app()

from __future__ import annotations

import json
from typing import Any

from fastapi import FastAPI

from globalgap.app.analyzer import GlobalGapAnalyzer
from globalgap.app.config import SAMPLE_PORTFOLIO_FILE
from globalgap.app.models import PortfolioPosition


def _load_sample_portfolio() -> list[dict[str, Any]]:
    return json.loads(SAMPLE_PORTFOLIO_FILE.read_text(encoding="utf-8"))


def create_app() -> FastAPI:
    app = FastAPI(
        title="GlobalGap",
        version="0.1.0",
        description="Reveal the valuation, currency, and earnings-growth gap between US-only portfolios and globally diversified ones.",
    )
    analyzer = GlobalGapAnalyzer()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/macro-data")
    async def macro_data() -> dict:
        return analyzer.macro_snapshot().model_dump()

    @app.get("/valuation-gap")
    async def valuation_gap() -> dict:
        return analyzer.macro_snapshot().valuation_gap.model_dump()

    @app.get("/dollar-cycle")
    async def dollar_cycle() -> dict:
        return analyzer.macro_snapshot().dollar_cycle.model_dump()

    @app.post("/analyze-portfolio")
    async def analyze_portfolio(positions: list[PortfolioPosition]) -> dict:
        return analyzer.analyze(positions).model_dump()

    @app.get("/sample-portfolio")
    async def sample_portfolio() -> list[dict[str, Any]]:
        return _load_sample_portfolio()

    return app


app = create_app()

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException

from true_cost_of_investing.app.config import (
    DEFAULT_ALTERNATIVE_PORTFOLIO_FILE,
    DEFAULT_ASSUMPTIONS_FILE,
    DEFAULT_PORTFOLIO_FILE,
)
from true_cost_of_investing.app.models import HoldingInput, PortfolioAssumptions
from true_cost_of_investing.app.schemas import AnalyzePortfolioCostRequest, ComparePortfoliosRequest
from true_cost_of_investing.app.services.analyzer import TrueCostAnalyzer


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def create_app() -> FastAPI:
    app = FastAPI(
        title="True Cost of Investing Calculator",
        version="0.1.0",
        description="Estimate the compounded long-term cost of fees, taxes, spreads, and hidden investing frictions.",
    )
    analyzer = TrueCostAnalyzer()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/sample-portfolio")
    async def sample_portfolio() -> list[dict[str, Any]]:
        return _load_json(DEFAULT_PORTFOLIO_FILE)

    @app.get("/sample-assumptions")
    async def sample_assumptions() -> dict[str, Any]:
        return _load_json(DEFAULT_ASSUMPTIONS_FILE)

    @app.get("/sample-result")
    async def sample_result() -> dict[str, Any]:
        holdings = [HoldingInput(**item) for item in _load_json(DEFAULT_PORTFOLIO_FILE)]
        assumptions = PortfolioAssumptions(**_load_json(DEFAULT_ASSUMPTIONS_FILE))
        return analyzer.analyze(holdings, assumptions).to_dict()

    @app.post("/analyze-portfolio-cost")
    async def analyze_portfolio_cost(request: AnalyzePortfolioCostRequest) -> dict[str, Any]:
        try:
            holdings = [HoldingInput(**item.model_dump()) for item in request.holdings]
            assumptions = PortfolioAssumptions(**request.assumptions.model_dump())
            return analyzer.analyze(holdings, assumptions).to_dict()
        except Exception as exc:  # pragma: no cover - FastAPI boundary
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/compare-portfolios")
    async def compare_portfolios(request: ComparePortfoliosRequest) -> dict[str, Any]:
        try:
            current = [HoldingInput(**item.model_dump()) for item in request.current_portfolio]
            alternative = [HoldingInput(**item.model_dump()) for item in request.alternative_portfolio]
            assumptions = PortfolioAssumptions(**request.assumptions.model_dump())
            return analyzer.compare(current, alternative, assumptions).to_dict()
        except Exception as exc:  # pragma: no cover - FastAPI boundary
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app()

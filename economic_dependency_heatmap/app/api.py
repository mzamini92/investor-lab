from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException

from economic_dependency_heatmap.app.config import DEFAULT_SAMPLE_PORTFOLIO
from economic_dependency_heatmap.app.exceptions import EconomicDependencyError
from economic_dependency_heatmap.app.schemas import AnalyzeDependenciesRequest
from economic_dependency_heatmap.app.services.analyzer import EconomicDependencyAnalyzer


def create_app() -> FastAPI:
    app = FastAPI(
        title="Economic Dependency Heatmap",
        version="0.1.0",
        description="Reveal what economies, demand centers, and macro engines an ETF portfolio really depends on.",
    )
    analyzer = EconomicDependencyAnalyzer()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/supported-etfs")
    async def supported_etfs() -> dict[str, list[str]]:
        return {"tickers": analyzer.data_provider.supported_etfs()}

    @app.get("/sample-portfolio")
    async def sample_portfolio() -> list[dict[str, Any]]:
        return DEFAULT_SAMPLE_PORTFOLIO

    @app.get("/sample-scenarios")
    async def sample_scenarios() -> list[dict[str, Any]]:
        return [scenario.to_dict() for scenario in analyzer.data_provider.get_scenarios()]

    @app.get("/sample-heatmap")
    async def sample_heatmap() -> list[dict[str, Any]]:
        return analyzer.analyze(DEFAULT_SAMPLE_PORTFOLIO).heatmap_ready_data

    @app.get("/sample-map-data")
    async def sample_map_data() -> list[dict[str, Any]]:
        return analyzer.analyze(DEFAULT_SAMPLE_PORTFOLIO).map_ready_data

    @app.post("/analyze-dependencies")
    async def analyze_dependencies(request: AnalyzeDependenciesRequest) -> dict[str, Any]:
        try:
            result = analyzer.analyze([position.model_dump() for position in request.positions])
        except EconomicDependencyError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result.to_dict()

    return app


app = create_app()

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException

from hedgefund_dependency_engine.app.config import DEFAULT_SAMPLE_PORTFOLIO
from hedgefund_dependency_engine.app.exceptions import HedgefundDependencyError, NewsProviderError
from hedgefund_dependency_engine.app.news.rss_provider import GoogleNewsRSSProvider
from hedgefund_dependency_engine.app.schemas import AnalyzePortfolioRequest
from hedgefund_dependency_engine.app.services.analyzer import HedgefundDependencyAnalyzer
from hedgefund_dependency_engine.app.services.live_news import headlines_to_context, suggest_dynamic_events_from_headlines
from hedgefund_dependency_engine.app.services.scenarios import event_templates_to_rows


def create_app() -> FastAPI:
    app = FastAPI(
        title="Hedgefund Dependency Engine",
        version="0.1.0",
        description="Look-through ETF analytics with factor loading, shock transmission, and graph concentration analysis.",
    )
    analyzer = HedgefundDependencyAnalyzer()
    news_provider = GoogleNewsRSSProvider()

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

    @app.get("/event-templates")
    async def event_templates() -> list[dict[str, Any]]:
        return event_templates_to_rows(analyzer.data_provider.get_event_templates())

    @app.get("/live-news-headlines")
    async def live_news_headlines(limit: int = 12) -> list[dict[str, Any]]:
        try:
            headlines = news_provider.fetch_headlines(limit=limit)
        except NewsProviderError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return [headline.to_dict() for headline in headlines]

    @app.get("/live-news-suggestions")
    async def live_news_suggestions(limit: int = 12) -> dict[str, Any]:
        try:
            headlines = news_provider.fetch_headlines(limit=limit)
        except NewsProviderError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        suggestions = suggest_dynamic_events_from_headlines(
            headlines,
            analyzer.data_provider.get_event_templates(),
        )
        return {
            "headlines": [headline.to_dict() for headline in headlines],
            "headline_context": headlines_to_context(headlines),
            "suggested_dynamic_events": suggestions,
        }

    @app.get("/sample-graph")
    async def sample_graph() -> dict[str, Any]:
        return analyzer.analyze(DEFAULT_SAMPLE_PORTFOLIO).graph_data

    @app.get("/sample-dependencies")
    async def sample_dependencies() -> list[dict[str, Any]]:
        return analyzer.analyze(DEFAULT_SAMPLE_PORTFOLIO).dependency_exposures

    @app.post("/analyze-portfolio")
    async def analyze_portfolio(request: AnalyzePortfolioRequest) -> dict[str, Any]:
        try:
            result = analyzer.analyze(
                [position.model_dump() for position in request.positions],
                selected_scenarios=request.scenario_names,
                dynamic_events=None if request.dynamic_events is None else [event.model_dump() for event in request.dynamic_events],
                headline_context=request.headline_context,
            )
        except HedgefundDependencyError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result.to_dict()

    return app


app = create_app()

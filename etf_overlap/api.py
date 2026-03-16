from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, PositiveFloat

from economic_dependency_heatmap.app.config import DEFAULT_SAMPLE_PORTFOLIO as DEFAULT_DEPENDENCY_SAMPLE_PORTFOLIO
from economic_dependency_heatmap.app.exceptions import EconomicDependencyError
from economic_dependency_heatmap.app.schemas import AnalyzeDependenciesRequest
from economic_dependency_heatmap.app.services.analyzer import EconomicDependencyAnalyzer
from etf_catalog.fetcher import load_etf_catalog
from etf_overlap.config import DEFAULT_DATA_DIR
from etf_overlap.config import DEFAULT_SAMPLE_PORTFOLIO
from etf_overlap.engine import PortfolioAnalyzer
from etf_overlap.exceptions import ETFOverlapError
from global_etf_exposure_map.app.config import DEFAULT_SAMPLE_PORTFOLIO as DEFAULT_GLOBAL_SAMPLE_PORTFOLIO
from global_etf_exposure_map.app.exceptions import GlobalExposureError
from global_etf_exposure_map.app.schemas import AnalyzeGlobalExposureRequest
from global_etf_exposure_map.app.services.analyzer import GlobalExposureAnalyzer
from hedgefund_dependency_engine.app.exceptions import NewsProviderError
from hedgefund_dependency_engine.app.news.rss_provider import GoogleNewsRSSProvider
from hedgefund_dependency_engine.app.services.analyzer import HedgefundDependencyAnalyzer
from hedgefund_dependency_engine.app.services.live_news import headlines_to_context, suggest_dynamic_events_from_headlines
from hedgefund_dependency_engine.app.services.scenarios import event_templates_to_rows


class PortfolioPositionRequest(BaseModel):
    ticker: str = Field(..., min_length=1)
    amount: PositiveFloat


class AnalyzePortfolioRequest(BaseModel):
    positions: list[PortfolioPositionRequest]


def create_app() -> FastAPI:
    app = FastAPI(
        title="ETF Hidden Overlap & Concentration Detector",
        version="0.1.0",
        description="Analyze ETF portfolios for hidden overlap, concentration, and false diversification.",
    )
    analyzer = PortfolioAnalyzer()
    global_exposure_analyzer = GlobalExposureAnalyzer()
    dependency_analyzer = EconomicDependencyAnalyzer()
    hedgefund_analyzer = HedgefundDependencyAnalyzer()
    news_provider = GoogleNewsRSSProvider()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/sample-portfolio")
    async def sample_portfolio() -> list[dict[str, Any]]:
        return DEFAULT_SAMPLE_PORTFOLIO

    @app.get("/supported-etfs")
    async def supported_etfs() -> dict[str, list[str]]:
        return {"tickers": analyzer.holdings_provider.supported_etfs()}

    @app.get("/catalog-etfs")
    async def catalog_etfs() -> list[dict[str, Any]]:
        return load_etf_catalog(DEFAULT_DATA_DIR.parent / "catalog" / "us_etf_catalog.csv").to_dict(orient="records")

    @app.get("/sample-global-portfolio")
    async def sample_global_portfolio() -> list[dict[str, Any]]:
        return DEFAULT_GLOBAL_SAMPLE_PORTFOLIO

    @app.get("/sample-dependency-portfolio")
    async def sample_dependency_portfolio() -> list[dict[str, Any]]:
        return DEFAULT_DEPENDENCY_SAMPLE_PORTFOLIO

    @app.post("/analyze-portfolio")
    async def analyze_portfolio(request: AnalyzePortfolioRequest) -> dict[str, Any]:
        try:
            result = analyzer.analyze([position.model_dump() for position in request.positions])
        except ETFOverlapError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result.to_dict()

    @app.get("/supported-global-etfs")
    async def supported_global_etfs() -> dict[str, list[str]]:
        return {"tickers": global_exposure_analyzer.holdings_provider.supported_etfs()}

    @app.get("/supported-dependency-etfs")
    async def supported_dependency_etfs() -> dict[str, list[str]]:
        return {"tickers": dependency_analyzer.data_provider.supported_etfs()}

    @app.get("/sample-scenarios")
    async def sample_scenarios() -> list[dict[str, Any]]:
        return [scenario.to_dict() for scenario in dependency_analyzer.data_provider.get_scenarios()]

    @app.get("/supported-hedgefund-etfs")
    async def supported_hedgefund_etfs() -> dict[str, list[str]]:
        return {"tickers": hedgefund_analyzer.data_provider.supported_etfs()}

    @app.get("/sample-hedgefund-portfolio")
    async def sample_hedgefund_portfolio() -> list[dict[str, Any]]:
        from hedgefund_dependency_engine.app.config import DEFAULT_SAMPLE_PORTFOLIO as DEFAULT_HF_SAMPLE_PORTFOLIO

        return DEFAULT_HF_SAMPLE_PORTFOLIO

    @app.get("/hedgefund-event-templates")
    async def hedgefund_event_templates() -> list[dict[str, Any]]:
        return event_templates_to_rows(hedgefund_analyzer.data_provider.get_event_templates())

    @app.get("/hedgefund-live-news-headlines")
    async def hedgefund_live_news_headlines(limit: int = 12) -> list[dict[str, Any]]:
        try:
            headlines = news_provider.fetch_headlines(limit=limit)
        except NewsProviderError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return [headline.to_dict() for headline in headlines]

    @app.get("/hedgefund-live-news-suggestions")
    async def hedgefund_live_news_suggestions(limit: int = 12) -> dict[str, Any]:
        try:
            headlines = news_provider.fetch_headlines(limit=limit)
        except NewsProviderError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {
            "headlines": [headline.to_dict() for headline in headlines],
            "headline_context": headlines_to_context(headlines),
            "suggested_dynamic_events": suggest_dynamic_events_from_headlines(
                headlines,
                hedgefund_analyzer.data_provider.get_event_templates(),
            ),
        }

    @app.get("/sample-map-data")
    async def sample_map_data() -> list[dict[str, Any]]:
        return global_exposure_analyzer.analyze(DEFAULT_GLOBAL_SAMPLE_PORTFOLIO).map_ready_data

    @app.get("/sample-dependency-heatmap")
    async def sample_dependency_heatmap() -> list[dict[str, Any]]:
        return dependency_analyzer.analyze(DEFAULT_DEPENDENCY_SAMPLE_PORTFOLIO).heatmap_ready_data

    @app.get("/sample-dependency-map-data")
    async def sample_dependency_map_data() -> list[dict[str, Any]]:
        return dependency_analyzer.analyze(DEFAULT_DEPENDENCY_SAMPLE_PORTFOLIO).map_ready_data

    @app.post("/analyze-global-exposure")
    async def analyze_global_exposure(request: AnalyzeGlobalExposureRequest) -> dict[str, Any]:
        try:
            result = global_exposure_analyzer.analyze([position.model_dump() for position in request.positions])
        except GlobalExposureError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result.to_dict()

    @app.post("/analyze-dependencies")
    async def analyze_dependencies(request: AnalyzeDependenciesRequest) -> dict[str, Any]:
        try:
            result = dependency_analyzer.analyze([position.model_dump() for position in request.positions])
        except EconomicDependencyError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result.to_dict()

    return app


app = create_app()

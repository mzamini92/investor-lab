import asyncio

from moat_watch.app.api import app
from moat_watch.app.schemas import AnalyzeCompanyMoatRequest


def _route_endpoint(path: str):
    for route in app.routes:
        if getattr(route, "path", None) == path:
            return route.endpoint
    raise AssertionError(f"Route not found: {path}")


def test_health_endpoint() -> None:
    endpoint = _route_endpoint("/health")
    assert asyncio.run(endpoint()) == {"status": "ok"}


def test_analyze_company_endpoint() -> None:
    endpoint = _route_endpoint("/analyze-company-moat")
    result = asyncio.run(endpoint(AnalyzeCompanyMoatRequest(ticker="MSFT", quarter="2025Q2")))
    assert result["ticker"] == "MSFT"
    assert "moat_health_label" in result

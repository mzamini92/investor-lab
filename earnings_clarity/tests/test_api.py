import asyncio

from fastapi.routing import APIRoute

from earnings_clarity.app.api import app


def _route(path: str, method: str):
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path == path and method.upper() in route.methods:
            return route.endpoint
    raise AssertionError(f"Route not found: {method} {path}")


def test_health_endpoint() -> None:
    endpoint = _route("/health", "GET")
    payload = asyncio.run(endpoint())
    assert payload["status"] == "ok"


def test_sample_summary_endpoint() -> None:
    endpoint = _route("/sample-summary/{ticker}", "GET")
    payload = asyncio.run(endpoint("AAPL"))
    assert payload["ticker"] == "AAPL"
    assert len(payload["five_point_summary"]) == 5


def test_sample_holdings_endpoint() -> None:
    endpoint = _route("/sample-holdings", "GET")
    payload = asyncio.run(endpoint())
    assert len(payload) >= 3

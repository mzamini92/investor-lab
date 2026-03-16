import asyncio

from value_check.app.api import app
from value_check.app.schemas import ValueCheckRequest


def _route_endpoint(path: str):
    for route in app.routes:
        if getattr(route, "path", None) == path:
            return route.endpoint
    raise AssertionError(f"Route not found: {path}")


def test_health_endpoint() -> None:
    endpoint = _route_endpoint("/health")
    assert asyncio.run(endpoint()) == {"status": "ok"}


def test_value_check_endpoint_returns_analysis() -> None:
    endpoint = _route_endpoint("/value-check")
    payload = asyncio.run(
        endpoint(
            ValueCheckRequest(
                ticker="MSFT",
                lookback_years=10,
                treasury_yield=0.042,
            )
        )
    )
    assert payload["ticker"] == "MSFT"
    assert "verdict" in payload
    assert "historical_comparison" in payload

import asyncio

from harvest_alert.app.api import app


def _route_endpoint(path: str):
    for route in app.routes:
        if getattr(route, "path", None) == path:
            return route.endpoint
    raise AssertionError(f"Route not found: {path}")


def test_health_endpoint() -> None:
    endpoint = _route_endpoint("/health")
    assert asyncio.run(endpoint()) == {"status": "ok"}


def test_sample_result_endpoint() -> None:
    endpoint = _route_endpoint("/sample-result")
    payload = asyncio.run(endpoint())
    assert "opportunities" in payload
    assert "estimated_total_tax_savings" in payload

import asyncio

from globalgap.app.api import create_app
from globalgap.app.models import PortfolioPosition


app = create_app()


def test_health() -> None:
    endpoint = next(route.endpoint for route in app.routes if getattr(route, "path", "") == "/health")
    payload = asyncio.run(endpoint())
    assert payload["status"] == "ok"


def test_analyze_portfolio() -> None:
    endpoint = next(route.endpoint for route in app.routes if getattr(route, "path", "") == "/analyze-portfolio")
    payload = asyncio.run(
        endpoint(
            [
                PortfolioPosition(ticker="VTI", quantity=120, price=285.0),
                PortfolioPosition(ticker="QQQ", quantity=20, price=515.0),
            ]
        )
    )
    assert "portfolio_exposure" in payload
    assert "recommendation" in payload

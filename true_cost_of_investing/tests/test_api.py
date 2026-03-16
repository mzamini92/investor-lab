import asyncio

from true_cost_of_investing.app.api import app
from true_cost_of_investing.app.schemas import ComparePortfoliosRequest


def _route(path: str):
    for route in app.routes:
        if getattr(route, "path", None) == path:
            return route
    raise AssertionError(f"Route {path} not found")


def test_health() -> None:
    payload = asyncio.run(_route("/health").endpoint())
    assert payload == {"status": "ok"}


def test_sample_result() -> None:
    payload = asyncio.run(_route("/sample-result").endpoint())
    assert "summary" in payload
    assert "annual_friction_breakdown" in payload


def test_compare_portfolios() -> None:
    current = asyncio.run(_route("/sample-portfolio").endpoint())
    assumptions = asyncio.run(_route("/sample-assumptions").endpoint())
    alternative = [
        {
            "ticker": "VTI",
            "amount": 14000,
            "expense_ratio": 0.0003,
            "asset_type": "ETF"
        },
        {
            "ticker": "VXUS",
            "amount": 9000,
            "expense_ratio": 0.0007,
            "asset_type": "ETF"
        }
    ]
    request = ComparePortfoliosRequest(
        current_portfolio=current,
        alternative_portfolio=alternative,
        assumptions=assumptions,
    )
    payload = asyncio.run(_route("/compare-portfolios").endpoint(request))
    assert "projected_savings" in payload

import asyncio

from economic_regime_translator.app.api import app
from economic_regime_translator.app.schemas import CompareSnapshotsRequest


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
    assert "regime_label" in payload
    assert "plain_english_summary" in payload


def test_compare_snapshots() -> None:
    current = asyncio.run(_route("/sample-current-snapshot").endpoint())
    history = asyncio.run(_route("/sample-history").endpoint())
    prior = {
        **current,
        "observation_date": "2025-11-30",
        "cpi_yoy": 3.3,
        "inflation_3m_annualized": 3.1,
        "term_spread_2s10s": -0.4,
        "high_yield_spread": 4.5,
        "earnings_revision_breadth": -0.08,
        "earnings_revision_momentum": -0.05,
    }
    request = CompareSnapshotsRequest(current_snapshot=current, prior_snapshot=prior, history_rows=history)
    payload = asyncio.run(_route("/compare-snapshots").endpoint(request))
    assert "transition_summary" in payload

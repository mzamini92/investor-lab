from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException

from economic_regime_translator.app.config import (
    DEFAULT_CURRENT_SNAPSHOT_FILE,
    DEFAULT_HISTORY_FILE,
    DEFAULT_PRIOR_SNAPSHOT_FILE,
)
from economic_regime_translator.app.models import MacroSnapshot
from economic_regime_translator.app.schemas import ClassifyRegimeRequest, CompareSnapshotsRequest
from economic_regime_translator.app.services.analyzer import EconomicRegimeAnalyzer


def _load_snapshot(path: Path) -> MacroSnapshot:
    return MacroSnapshot(**json.loads(path.read_text(encoding="utf-8")))


def _load_history(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Economic Regime Translator",
        version="0.1.0",
        description="Translate macro data into a plain-English economic regime with historical analogs and portfolio implications.",
    )
    analyzer = EconomicRegimeAnalyzer()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/sample-current-snapshot")
    async def sample_current_snapshot() -> dict[str, Any]:
        return json.loads(DEFAULT_CURRENT_SNAPSHOT_FILE.read_text(encoding="utf-8"))

    @app.get("/sample-history")
    async def sample_history() -> list[dict[str, Any]]:
        return _load_history(DEFAULT_HISTORY_FILE).to_dict(orient="records")

    @app.get("/sample-latest-history-snapshot")
    async def sample_latest_history_snapshot() -> dict[str, Any]:
        history = _load_history(DEFAULT_HISTORY_FILE)
        return analyzer.latest_snapshot_from_history(history).to_dict()

    @app.get("/sample-result")
    async def sample_result() -> dict[str, Any]:
        return analyzer.classify(_load_snapshot(DEFAULT_CURRENT_SNAPSHOT_FILE), _load_history(DEFAULT_HISTORY_FILE)).to_dict()

    @app.post("/classify-regime")
    async def classify_regime(request: ClassifyRegimeRequest) -> dict[str, Any]:
        try:
            snapshot = MacroSnapshot(**request.current_snapshot.model_dump())
            history = pd.DataFrame(request.history_rows) if request.history_rows else _load_history(DEFAULT_HISTORY_FILE)
            return analyzer.classify(snapshot, history).to_dict()
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/compare-snapshots")
    async def compare_snapshots(request: CompareSnapshotsRequest) -> dict[str, Any]:
        try:
            current = MacroSnapshot(**request.current_snapshot.model_dump())
            prior = MacroSnapshot(**request.prior_snapshot.model_dump())
            history = pd.DataFrame(request.history_rows) if request.history_rows else _load_history(DEFAULT_HISTORY_FILE)
            return analyzer.compare(current, prior, history).to_dict()
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app()

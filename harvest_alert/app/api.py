from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException

from harvest_alert.app.config import DEFAULT_SCAN_DATE
from harvest_alert.app.models import Account, Position, ReplacementSecurity, TaxAssumptions, TaxLot, Transaction
from harvest_alert.app.providers.brokerage_provider import LocalBrokerageProvider
from harvest_alert.app.schemas import EvaluateSinglePositionRequest, ScanHarvestRequest
from harvest_alert.app.services.analyzer import HarvestAlertAnalyzer


def create_app() -> FastAPI:
    app = FastAPI(title="HarvestAlert", version="0.1.0", description="Tax-loss harvesting opportunity scanner for taxable brokerage accounts.")
    provider = LocalBrokerageProvider()
    analyzer = HarvestAlertAnalyzer(provider)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/sample-accounts")
    async def sample_accounts() -> list[dict[str, Any]]:
        return [item.__dict__ for item in provider.get_accounts()]

    @app.get("/sample-positions")
    async def sample_positions() -> list[dict[str, Any]]:
        return [item.__dict__ for item in provider.get_positions()]

    @app.get("/sample-replacements")
    async def sample_replacements() -> list[dict[str, Any]]:
        return [item.__dict__ for item in provider.get_replacements()]

    @app.get("/sample-result")
    async def sample_result() -> dict[str, Any]:
        return analyzer.sample_scan().to_dict()

    @app.post("/scan-harvest-opportunities")
    async def scan_harvest_opportunities(request: ScanHarvestRequest) -> dict[str, Any]:
        try:
            result = analyzer.scan(
                accounts=[Account(**item.model_dump()) for item in request.accounts],
                positions=[Position(**item.model_dump()) for item in request.positions],
                lots=[TaxLot(**item.model_dump()) for item in request.lots],
                transactions=[Transaction(**item.model_dump()) for item in request.transactions],
                tax_assumptions=TaxAssumptions(**request.tax_assumptions.model_dump()),
                replacement_universe=[ReplacementSecurity(**item.model_dump()) for item in request.replacement_universe],
                scan_date=request.scan_date or DEFAULT_SCAN_DATE,
            )
            return result.to_dict()
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/evaluate-single-position")
    async def evaluate_single_position(request: EvaluateSinglePositionRequest) -> dict[str, Any]:
        try:
            result = analyzer.evaluate_single_position(
                position=Position(**request.position.model_dump()),
                lots=[TaxLot(**item.model_dump()) for item in request.lots],
                transactions=[Transaction(**item.model_dump()) for item in request.transactions],
                tax_assumptions=TaxAssumptions(**request.tax_assumptions.model_dump()),
                replacement_universe=[ReplacementSecurity(**item.model_dump()) for item in request.replacement_universe],
                account=Account(**request.account.model_dump()) if request.account else None,
                scan_date=request.scan_date or DEFAULT_SCAN_DATE,
            )
            return result.to_dict()
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app()

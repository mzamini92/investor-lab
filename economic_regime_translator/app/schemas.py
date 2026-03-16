from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class MacroSnapshotRequest(BaseModel):
    observation_date: str
    fed_funds_rate: float
    fed_funds_3m_change: float
    cpi_yoy: float
    core_cpi_yoy: float
    inflation_3m_annualized: float
    unemployment_rate: float
    unemployment_3m_change: float
    payroll_trend: Optional[float] = None
    ism_manufacturing: float
    ism_services: Optional[float] = None
    real_policy_rate: Optional[float] = None
    yield_2y: float
    yield_10y: float
    term_spread_2s10s: float
    term_spread_3m10y: Optional[float] = None
    high_yield_spread: float
    investment_grade_spread: Optional[float] = None
    earnings_revision_breadth: float
    earnings_revision_momentum: Optional[float] = None
    financial_conditions_index: Optional[float] = None
    equity_breadth: Optional[float] = None
    usd_index_change: Optional[float] = None
    oil_price_change: Optional[float] = None


class ClassifyRegimeRequest(BaseModel):
    current_snapshot: MacroSnapshotRequest
    history_rows: Optional[list[dict]] = None


class CompareSnapshotsRequest(BaseModel):
    current_snapshot: MacroSnapshotRequest
    prior_snapshot: MacroSnapshotRequest
    history_rows: Optional[list[dict]] = None

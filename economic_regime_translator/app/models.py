from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class MacroSnapshot:
    observation_date: str
    fed_funds_rate: float
    fed_funds_3m_change: float
    cpi_yoy: float
    core_cpi_yoy: float
    inflation_3m_annualized: float
    unemployment_rate: float
    unemployment_3m_change: float
    payroll_trend: Optional[float] = None
    ism_manufacturing: float = 50.0
    ism_services: Optional[float] = None
    real_policy_rate: Optional[float] = None
    yield_2y: float = 0.0
    yield_10y: float = 0.0
    term_spread_2s10s: float = 0.0
    term_spread_3m10y: Optional[float] = None
    high_yield_spread: float = 0.0
    investment_grade_spread: Optional[float] = None
    earnings_revision_breadth: float = 0.0
    earnings_revision_momentum: Optional[float] = None
    financial_conditions_index: Optional[float] = None
    equity_breadth: Optional[float] = None
    usd_index_change: Optional[float] = None
    oil_price_change: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HistoricalAnalog:
    observation_date: str
    similarity_score: float
    regime_label: str
    summary: str
    asset_behavior: dict[str, Any]


@dataclass
class RegimeAnalysisResult:
    observation_date: str
    regime_label: str
    sub_regime_labels: list[str]
    confidence_score: float
    scorecard: dict[str, float]
    indicator_states: dict[str, Any]
    primary_drivers: list[str]
    changed_signals: list[str]
    historical_analogs: list[dict[str, Any]]
    portfolio_implications: dict[str, Any]
    risk_flags: list[str]
    watch_items: list[str]
    plain_english_summary: dict[str, Any]
    visualization_data: dict[str, Any]
    analysis_metadata: dict[str, Any] = field(
        default_factory=lambda: {"generated_at": datetime.now(timezone.utc).isoformat()}
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SnapshotComparisonResult:
    prior_regime_label: str
    current_regime_label: str
    transition_label: str
    transition_summary: str
    changed_indicators: list[dict[str, Any]]
    strongest_positive_shift: str
    strongest_negative_shift: str
    current_analysis: dict[str, Any]
    prior_analysis: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

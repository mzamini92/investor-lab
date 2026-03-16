from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class ValuationSnapshot:
    ticker: str
    company_name: str
    asset_type: str
    sector: str
    industry: str
    market_cap: float
    enterprise_value: Optional[float]
    price: float
    shares_outstanding: Optional[float]
    net_income_ttm: Optional[float]
    ebitda_ttm: Optional[float]
    revenue_ttm: Optional[float]
    free_cash_flow_ttm: Optional[float]
    book_value: Optional[float]
    earnings_growth_estimate: Optional[float] = None
    current_treasury_yield: Optional[float] = None
    peer_group: Optional[str] = None
    expense_ratio: Optional[float] = None
    distribution_yield: Optional[float] = None
    weighted_average_market_cap: Optional[float] = None
    valuation_proxy_note: Optional[str] = None

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        self.asset_type = self.asset_type.lower().strip()
        if self.asset_type not in {"stock", "etf"}:
            raise ValueError("asset_type must be 'stock' or 'etf'")
        if self.market_cap <= 0 or self.price <= 0:
            raise ValueError(f"market_cap and price must be positive for {self.ticker}")


@dataclass
class MetricResult:
    name: str
    value: Optional[float]
    available: bool
    caveat: Optional[str] = None


@dataclass
class ValueCheckResult:
    ticker: str
    company_name: str
    asset_type: str
    sector: str
    industry: str
    current_metrics: dict[str, Any]
    historical_comparison: list[dict[str, Any]]
    peer_comparison: list[dict[str, Any]]
    treasury_context: dict[str, Any]
    composite_score: float
    confidence_score: float
    verdict: dict[str, Any]
    implied_expectations_summary: dict[str, Any]
    long_term_takeaway: str
    watch_items: list[str]
    caveats: list[str]
    plain_english_summary: dict[str, Any]
    visualization_data: dict[str, Any]
    analysis_metadata: dict[str, Any] = field(
        default_factory=lambda: {"generated_at": datetime.now(timezone.utc).isoformat()}
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

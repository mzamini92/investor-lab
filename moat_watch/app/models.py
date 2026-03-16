from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class WatchlistItem:
    ticker: str
    purchase_thesis_notes: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    benchmark_peers: Optional[list[str]] = None
    company_category: Optional[str] = None
    historical_baseline_quarter: Optional[str] = None

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        if not self.ticker:
            raise ValueError("Ticker cannot be empty.")


@dataclass
class QuarterlyMetrics:
    ticker: str
    company_name: str
    sector: str
    industry: str
    fiscal_year: int
    fiscal_quarter: int
    revenue: float
    gross_profit: float
    operating_margin: float
    free_cash_flow: float
    invested_capital: float
    roic: float
    estimated_wacc: float
    r_and_d_expense: float
    sales_and_marketing_expense: float
    capex: float
    same_store_sales: Optional[float] = None
    units_sold: Optional[float] = None
    average_selling_price: Optional[float] = None
    revenue_per_unit: Optional[float] = None
    volume_growth: Optional[float] = None
    price_realization: Optional[float] = None
    market_share: Optional[float] = None
    inventory_growth: Optional[float] = None
    receivables_growth: Optional[float] = None
    customer_acquisition_cost: Optional[float] = None
    ltv_to_cac: Optional[float] = None
    gross_margin: Optional[float] = None
    roic_wacc_spread: Optional[float] = None
    r_and_d_as_pct_revenue: Optional[float] = None
    sga_as_pct_revenue: Optional[float] = None
    capex_as_pct_revenue: Optional[float] = None
    market_share_change: Optional[float] = None

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        if not self.ticker:
            raise ValueError("Ticker cannot be empty.")

    @property
    def quarter_label(self) -> str:
        return f"{self.fiscal_year}Q{self.fiscal_quarter}"


@dataclass
class CommentaryRecord:
    ticker: str
    quarter: str
    raw_commentary_text: str
    mentions_pricing_pressure: bool = False
    mentions_competition: bool = False
    mentions_promotions: bool = False
    mentions_market_share_gain: bool = False
    mentions_market_share_loss: bool = False
    mentions_customer_weakness: bool = False
    mentions_cost_pressure: bool = False
    mentions_innovation_strength: bool = False

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()


@dataclass
class SignalResult:
    signal_name: str
    current_status: str
    change_direction: str
    strength_score: float
    evidence: str
    value: Optional[float] = None


@dataclass
class MoatAnalysisResult:
    ticker: str
    company_name: str
    fiscal_quarter: str
    fiscal_year: int
    moat_health_score: float
    moat_health_label: str
    score_change_qoq: Optional[float]
    score_change_yoy: Optional[float]
    signal_breakdown: list[dict[str, Any]]
    peer_comparison: list[dict[str, Any]]
    transition_label: str
    alert_flags: list[str]
    commentary_findings: dict[str, Any]
    caution_heuristic: dict[str, Any]
    short_verdict: str
    long_term_takeaway: str
    watch_items: list[str]
    plain_english_summary: dict[str, Any]
    historical_moat_scores: list[dict[str, Any]]
    visualization_data: dict[str, Any]
    analysis_metadata: dict[str, Any] = field(
        default_factory=lambda: {"generated_at": datetime.now(timezone.utc).isoformat()}
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WatchlistQuarterResult:
    quarter: str
    analyses: list[dict[str, Any]]
    alert_digest: list[str]
    summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

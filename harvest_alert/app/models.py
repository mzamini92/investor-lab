from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class Account:
    account_id: str
    account_name: str
    account_type: str
    taxable_flag: bool
    owner_id: Optional[str] = None

    def __post_init__(self) -> None:
        self.account_id = self.account_id.strip()
        if not self.account_id:
            raise ValueError("account_id cannot be empty")


@dataclass
class Position:
    account_id: str
    ticker: str
    security_name: str
    asset_type: str
    quantity: float
    current_price: float
    market_value: float
    cost_basis_total: Optional[float] = None
    unrealized_gain_loss: Optional[float] = None
    sector: Optional[str] = None
    asset_class: Optional[str] = None
    strategy_bucket: Optional[str] = None
    expense_ratio: Optional[float] = None

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()


@dataclass
class TaxLot:
    account_id: str
    ticker: str
    lot_id: str
    acquisition_date: str
    quantity: float
    cost_basis_per_share: float
    total_cost_basis: Optional[float]
    current_price: float
    unrealized_gain_loss: Optional[float]
    short_term_or_long_term: Optional[str] = None

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        self.lot_id = self.lot_id.strip()


@dataclass
class Transaction:
    account_id: str
    trade_date: str
    ticker: str
    transaction_type: str
    quantity: float
    price: float
    amount: float
    side: str
    security_name: Optional[str] = None
    recurring_flag: bool = False

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()


@dataclass
class TaxAssumptions:
    federal_short_term_rate: float
    federal_long_term_rate: float
    state_tax_rate: float = 0.0
    marginal_income_tax_rate: Optional[float] = None
    default_loss_benefit_rate: float = 0.25
    minimum_loss_dollar_threshold: float = 250.0
    minimum_tax_savings_threshold: float = 75.0
    trading_cost_bps: float = 2.0
    bid_ask_cost_bps: float = 3.0
    slippage_bps: float = 2.0
    holding_period_days_for_replacement: int = 31

    @property
    def effective_short_term_rate(self) -> float:
        return (self.marginal_income_tax_rate or self.federal_short_term_rate) + self.state_tax_rate

    @property
    def effective_long_term_rate(self) -> float:
        return self.federal_long_term_rate + self.state_tax_rate


@dataclass
class ReplacementSecurity:
    ticker: str
    security_name: str
    asset_class: str
    region: str
    market_cap_focus: str
    style: str
    factor_tilt: Optional[str]
    sector_focus: Optional[str]
    expense_ratio: float
    benchmark_index: str
    strategy_tags: list[str]
    similar_to: list[str] = field(default_factory=list)
    prohibited_as_replacement_for: list[str] = field(default_factory=list)
    holdings_similarity_score: Optional[float] = None

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        self.similar_to = [item.upper() for item in self.similar_to]
        self.prohibited_as_replacement_for = [item.upper() for item in self.prohibited_as_replacement_for]


@dataclass
class HarvestOpportunity:
    ticker: str
    account_id: str
    lot_id: Optional[str]
    harvestable_loss: float
    loss_pct_from_basis: float
    tax_rate_used: float
    estimated_tax_savings: float
    transaction_cost_estimate: float
    net_estimated_benefit: float
    wash_sale_risk_level: str
    conflict_summary: str
    recommended_replacement: Optional[dict[str, Any]]
    replacement_similarity_score: Optional[float]
    exposure_drift_summary: str
    hold_days_recommendation: int
    opportunity_score: float
    alert_text: str
    applicable_term: str


@dataclass
class HarvestScanResult:
    scan_date: str
    accounts_scanned: list[str]
    opportunities: list[dict[str, Any]]
    no_action_positions: list[dict[str, Any]]
    wash_sale_conflicts: list[dict[str, Any]]
    replacement_recommendations: list[dict[str, Any]]
    estimated_total_tax_savings: float
    estimated_total_net_benefit: float
    data_completeness_flags: list[str]
    disclaimers: list[str]
    plain_english_summary: dict[str, Any]
    visualization_data: dict[str, Any]
    analysis_metadata: dict[str, Any] = field(
        default_factory=lambda: {"generated_at": datetime.now(timezone.utc).isoformat()}
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

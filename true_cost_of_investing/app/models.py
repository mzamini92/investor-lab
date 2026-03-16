from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from true_cost_of_investing.app.utils.validation import validate_positive


ACCOUNT_TYPES = {"taxable", "ira", "roth_ira", "401k"}


@dataclass
class HoldingInput:
    ticker: str
    amount: float
    expense_ratio: float
    asset_type: str
    dividend_yield: float = 0.0
    qualified_dividend_yield: float = 0.0
    nonqualified_dividend_yield: float = 0.0
    annual_turnover_rate: float = 0.0
    estimated_spread_cost_bps: float = 0.0
    expected_distribution_tax_character: Optional[str] = None
    advisory_fee_override: Optional[float] = None
    withholding_tax_rate: Optional[float] = None
    layered_fee_ratio: float = 0.0

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        self.asset_type = self.asset_type.strip()
        validate_positive(self.amount, f"amount for {self.ticker}")
        if self.expense_ratio < 0:
            raise ValueError(f"expense_ratio cannot be negative for {self.ticker}")
        if self.dividend_yield < 0 or self.qualified_dividend_yield < 0 or self.nonqualified_dividend_yield < 0:
            raise ValueError(f"dividend yields cannot be negative for {self.ticker}")
        if self.annual_turnover_rate < 0:
            raise ValueError(f"annual_turnover_rate cannot be negative for {self.ticker}")
        if self.estimated_spread_cost_bps < 0:
            raise ValueError(f"estimated_spread_cost_bps cannot be negative for {self.ticker}")
        if self.layered_fee_ratio < 0:
            raise ValueError(f"layered_fee_ratio cannot be negative for {self.ticker}")


@dataclass
class PortfolioAssumptions:
    monthly_contribution: float
    annual_gross_return: float
    investment_horizon_years: int
    account_type: str
    qualified_dividend_tax_rate: float = 0.15
    ordinary_income_tax_rate: float = 0.24
    capital_gains_tax_rate: float = 0.15
    state_tax_rate: float = 0.0
    annual_advisory_fee: float = 0.0
    annual_cash_drag: float = 0.0
    rebalance_frequency_per_year: int = 1
    commission_per_trade: float = 0.0
    slippage_bps: float = 0.0
    tax_loss_harvesting_benefit: float = 0.0
    contribution_growth_rate: float = 0.0
    inflation_rate: float = 0.0

    def __post_init__(self) -> None:
        validate_positive(self.investment_horizon_years, "investment_horizon_years")
        if self.account_type not in ACCOUNT_TYPES:
            raise ValueError(f"account_type must be one of {sorted(ACCOUNT_TYPES)}")
        if self.monthly_contribution < 0:
            raise ValueError("monthly_contribution cannot be negative")
        if self.rebalance_frequency_per_year < 0:
            raise ValueError("rebalance_frequency_per_year cannot be negative")
        if self.commission_per_trade < 0:
            raise ValueError("commission_per_trade cannot be negative")
        if self.slippage_bps < 0:
            raise ValueError("slippage_bps cannot be negative")


@dataclass
class NormalizedHolding:
    ticker: str
    amount: float
    weight: float
    expense_ratio: float
    asset_type: str
    dividend_yield: float
    qualified_dividend_yield: float
    nonqualified_dividend_yield: float
    annual_turnover_rate: float
    estimated_spread_cost_bps: float
    advisory_fee_override: Optional[float]
    withholding_tax_rate: float
    layered_fee_ratio: float


@dataclass
class AnnualCostComponent:
    category: str
    annual_rate: float
    annual_cost_dollars: float
    cost_type: str
    description: str


@dataclass
class ProjectionPoint:
    year: int
    gross_value: float
    net_value: float
    cumulative_direct_costs: float
    cumulative_lost_wealth: float


@dataclass
class CategoryAttribution:
    category: str
    direct_cost_dollars: float
    attributable_ending_value_loss: float
    attributable_percent_of_total_loss: float


@dataclass
class CostAnalysisResult:
    normalized_holdings: list[dict[str, Any]]
    blended_cost_metrics: dict[str, Any]
    annual_friction_breakdown: list[dict[str, Any]]
    per_holding_cost_breakdown: list[dict[str, Any]]
    projected_ending_values: dict[str, Any]
    dollars_lost_by_category: list[dict[str, Any]]
    timeline: list[dict[str, Any]]
    comparison_table: list[dict[str, Any]]
    summary: dict[str, Any]
    insights: list[str]
    recommendations: list[str]
    chart_data: dict[str, Any]
    analysis_metadata: dict[str, Any] = field(
        default_factory=lambda: {"generated_at": datetime.now(timezone.utc).isoformat()}
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ComparisonResult:
    current: CostAnalysisResult
    alternative: CostAnalysisResult
    projected_savings: dict[str, Any]
    insights: list[str]
    recommendations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "current": self.current.to_dict(),
            "alternative": self.alternative.to_dict(),
            "projected_savings": self.projected_savings,
            "insights": self.insights,
            "recommendations": self.recommendations,
        }

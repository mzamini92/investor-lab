from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from etf_overlap.exceptions import ValidationError


@dataclass
class PortfolioPosition:
    ticker: str
    amount: float

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        if not self.ticker:
            raise ValidationError("Portfolio position ticker cannot be empty.")
        if self.amount <= 0:
            raise ValidationError(f"Portfolio position amount must be positive for {self.ticker}.")


@dataclass
class HoldingRecord:
    stock_ticker: str
    company_name: str
    weight: float
    sector: str
    country: Optional[str] = None
    market_cap: Optional[float] = None
    style_box: Optional[str] = None

    def __post_init__(self) -> None:
        self.stock_ticker = self.stock_ticker.upper().strip()
        self.company_name = self.company_name.strip()
        self.sector = self.sector.strip() or "Unknown"
        self.country = (self.country or "Unknown").strip()
        self.style_box = (self.style_box or "Unknown").strip()

        if not self.stock_ticker:
            raise ValidationError("Holding stock ticker cannot be empty.")
        if not self.company_name:
            raise ValidationError(f"Holding company name is required for {self.stock_ticker}.")
        if self.weight < 0:
            raise ValidationError(f"Holding weight cannot be negative for {self.stock_ticker}.")


@dataclass
class ETFHoldings:
    ticker: str
    holdings: list[HoldingRecord]

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        if not self.ticker:
            raise ValidationError("ETF holdings ticker cannot be empty.")
        if not self.holdings:
            raise ValidationError(f"ETF {self.ticker} has no holdings.")

    def normalized(self) -> "ETFHoldings":
        total_weight = sum(holding.weight for holding in self.holdings)
        if total_weight <= 0:
            raise ValidationError(f"ETF {self.ticker} has non-positive total holding weight.")
        if abs(total_weight - 1.0) < 1e-9:
            return self

        normalized_holdings = [
            HoldingRecord(
                stock_ticker=holding.stock_ticker,
                company_name=holding.company_name,
                weight=holding.weight / total_weight,
                sector=holding.sector,
                country=holding.country,
                market_cap=holding.market_cap,
                style_box=holding.style_box,
            )
            for holding in self.holdings
        ]
        return ETFHoldings(ticker=self.ticker, holdings=normalized_holdings)


@dataclass
class AnalysisResult:
    normalized_portfolio: list[dict[str, Any]]
    underlying_exposures: list[dict[str, Any]]
    overlap_matrix: dict[str, dict[str, dict[str, Any]]]
    overlap_pairs: list[dict[str, Any]]
    concentration_metrics: dict[str, Any]
    sector_exposures: list[dict[str, Any]]
    country_exposures: list[dict[str, Any]]
    style_exposures: list[dict[str, Any]]
    mag7_exposure: dict[str, Any]
    warnings: list[str]
    summary_insights: list[str]
    optimization_suggestions: list[str]
    diversification_score: float
    hidden_concentration_score: float
    redundancy_index: float
    score_breakdown: dict[str, float]
    analysis_metadata: dict[str, Any] = field(
        default_factory=lambda: {"generated_at": datetime.now(timezone.utc).isoformat()}
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

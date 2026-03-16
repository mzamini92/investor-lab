from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from global_etf_exposure_map.app.exceptions import ValidationError


@dataclass
class PortfolioPosition:
    ticker: str
    amount: float

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        if not self.ticker:
            raise ValidationError("Portfolio position ticker cannot be empty.")
        if self.amount <= 0:
            raise ValidationError(f"Amount must be positive for {self.ticker}.")


@dataclass
class HoldingRecord:
    etf_ticker: str
    underlying_ticker: str
    company_name: str
    holding_weight: float
    sector: str
    country_domicile: str
    region: str
    currency: str
    market_cap_bucket: str
    revenue_north_america: float = 0.0
    revenue_europe: float = 0.0
    revenue_asia_pacific: float = 0.0
    revenue_emerging_markets: float = 0.0
    revenue_latin_america: float = 0.0
    revenue_middle_east_africa: float = 0.0
    country_code: str = ""

    def __post_init__(self) -> None:
        self.etf_ticker = self.etf_ticker.upper().strip()
        self.underlying_ticker = self.underlying_ticker.upper().strip()
        self.company_name = self.company_name.strip()
        self.sector = self.sector.strip() or "Unknown"
        self.country_domicile = self.country_domicile.strip() or "Unknown"
        self.region = self.region.strip() or "Unknown"
        self.currency = self.currency.upper().strip() or "Unknown"
        self.market_cap_bucket = self.market_cap_bucket.strip() or "Unknown"
        self.country_code = self.country_code.upper().strip()

        if not self.etf_ticker or not self.underlying_ticker:
            raise ValidationError("ETF ticker and underlying ticker are required.")
        if self.holding_weight < 0:
            raise ValidationError(f"Holding weight cannot be negative for {self.underlying_ticker}.")

        revenue_total = (
            self.revenue_north_america
            + self.revenue_europe
            + self.revenue_asia_pacific
            + self.revenue_emerging_markets
            + self.revenue_latin_america
            + self.revenue_middle_east_africa
        )
        if revenue_total and abs(revenue_total - 1.0) > 0.02:
            raise ValidationError(
                f"Revenue shares for {self.underlying_ticker} must sum approximately to 1.0; got {revenue_total:.4f}."
            )


@dataclass
class ETFHoldings:
    ticker: str
    label_region: str
    label_focus: str
    holdings: list[HoldingRecord]

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        if not self.ticker:
            raise ValidationError("ETF ticker cannot be empty.")
        if not self.holdings:
            raise ValidationError(f"No holdings available for ETF {self.ticker}.")

    def normalized(self) -> "ETFHoldings":
        total_weight = sum(record.holding_weight for record in self.holdings)
        if total_weight <= 0:
            raise ValidationError(f"ETF {self.ticker} has non-positive holding weight total.")
        if abs(total_weight - 1.0) < 1e-9:
            return self

        normalized_holdings = [
            HoldingRecord(
                etf_ticker=record.etf_ticker,
                underlying_ticker=record.underlying_ticker,
                company_name=record.company_name,
                holding_weight=record.holding_weight / total_weight,
                sector=record.sector,
                country_domicile=record.country_domicile,
                region=record.region,
                currency=record.currency,
                market_cap_bucket=record.market_cap_bucket,
                revenue_north_america=record.revenue_north_america,
                revenue_europe=record.revenue_europe,
                revenue_asia_pacific=record.revenue_asia_pacific,
                revenue_emerging_markets=record.revenue_emerging_markets,
                revenue_latin_america=record.revenue_latin_america,
                revenue_middle_east_africa=record.revenue_middle_east_africa,
                country_code=record.country_code,
            )
            for record in self.holdings
        ]
        return ETFHoldings(
            ticker=self.ticker,
            label_region=self.label_region,
            label_focus=self.label_focus,
            holdings=normalized_holdings,
        )


@dataclass
class GlobalExposureAnalysisResult:
    normalized_portfolio_weights: list[dict[str, Any]]
    underlying_company_exposures: list[dict[str, Any]]
    country_exposure_table: list[dict[str, Any]]
    region_exposure_table: list[dict[str, Any]]
    currency_exposure_table: list[dict[str, Any]]
    sector_exposure_table: list[dict[str, Any]]
    market_cap_exposure_table: list[dict[str, Any]]
    country_concentration_metrics: dict[str, Any]
    region_concentration_metrics: dict[str, Any]
    domicile_vs_revenue_exposure: list[dict[str, Any]]
    sector_region_matrix: list[dict[str, Any]]
    map_ready_data: list[dict[str, Any]]
    dashboard_summary: dict[str, Any]
    global_dependence_score: float
    economic_reality_gap: float
    warnings: list[str]
    summary_insights: list[str]
    recommendations: list[str]
    analysis_metadata: dict[str, Any] = field(
        default_factory=lambda: {"generated_at": datetime.now(timezone.utc).isoformat()}
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

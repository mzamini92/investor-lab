from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from economic_dependency_heatmap.app.config import DEPENDENCY_COLUMNS, REVENUE_COLUMNS
from economic_dependency_heatmap.app.exceptions import ValidationError


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
class CompanyProfile:
    underlying_ticker: str
    revenue_us: float = 0.0
    revenue_europe: float = 0.0
    revenue_china: float = 0.0
    revenue_apac_ex_china: float = 0.0
    revenue_japan: float = 0.0
    revenue_latam: float = 0.0
    revenue_mea: float = 0.0
    revenue_other: float = 0.0
    us_consumer: float = 0.0
    china_demand: float = 0.0
    europe_demand: float = 0.0
    ai_capex: float = 0.0
    cloud_spending: float = 0.0
    global_semiconductors: float = 0.0
    energy_prices: float = 0.0
    industrial_capex: float = 0.0
    emerging_market_growth: float = 0.0
    healthcare_spending: float = 0.0
    financial_conditions: float = 0.0
    usd_strength: float = 0.0
    interest_rate_sensitivity: float = 0.0
    profile_source: str = "inferred"

    def __post_init__(self) -> None:
        self.underlying_ticker = self.underlying_ticker.upper().strip()
        if not self.underlying_ticker:
            raise ValidationError("Company profile ticker cannot be empty.")

        revenue_total = sum(float(getattr(self, column_name)) for column_name in REVENUE_COLUMNS.values())
        if revenue_total and abs(revenue_total - 1.0) > 0.03:
            raise ValidationError(
                f"Revenue shares for {self.underlying_ticker} must sum approximately to 1.0; got {revenue_total:.4f}."
            )

        for dependency_name in DEPENDENCY_COLUMNS:
            dependency_value = float(getattr(self, dependency_name))
            if dependency_value < 0 or dependency_value > 1:
                raise ValidationError(
                    f"Dependency score {dependency_name} for {self.underlying_ticker} must be between 0 and 1."
                )

    def revenue_profile(self) -> dict[str, float]:
        return {bucket: float(getattr(self, column_name)) for bucket, column_name in REVENUE_COLUMNS.items()}

    def dependency_profile(self) -> dict[str, float]:
        return {dependency_name: float(getattr(self, dependency_name)) for dependency_name in DEPENDENCY_COLUMNS}


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
    country_code: str
    revenue_us: float = 0.0
    revenue_europe: float = 0.0
    revenue_china: float = 0.0
    revenue_apac_ex_china: float = 0.0
    revenue_japan: float = 0.0
    revenue_latam: float = 0.0
    revenue_mea: float = 0.0
    revenue_other: float = 0.0
    us_consumer: float = 0.0
    china_demand: float = 0.0
    europe_demand: float = 0.0
    ai_capex: float = 0.0
    cloud_spending: float = 0.0
    global_semiconductors: float = 0.0
    energy_prices: float = 0.0
    industrial_capex: float = 0.0
    emerging_market_growth: float = 0.0
    healthcare_spending: float = 0.0
    financial_conditions: float = 0.0
    usd_strength: float = 0.0
    interest_rate_sensitivity: float = 0.0
    profile_source: str = "inferred"

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
        self.profile_source = self.profile_source.strip() or "inferred"

        if not self.etf_ticker or not self.underlying_ticker:
            raise ValidationError("ETF ticker and underlying ticker are required.")
        if self.holding_weight < 0:
            raise ValidationError(f"Holding weight cannot be negative for {self.underlying_ticker}.")

        CompanyProfile(
            underlying_ticker=self.underlying_ticker,
            revenue_us=self.revenue_us,
            revenue_europe=self.revenue_europe,
            revenue_china=self.revenue_china,
            revenue_apac_ex_china=self.revenue_apac_ex_china,
            revenue_japan=self.revenue_japan,
            revenue_latam=self.revenue_latam,
            revenue_mea=self.revenue_mea,
            revenue_other=self.revenue_other,
            us_consumer=self.us_consumer,
            china_demand=self.china_demand,
            europe_demand=self.europe_demand,
            ai_capex=self.ai_capex,
            cloud_spending=self.cloud_spending,
            global_semiconductors=self.global_semiconductors,
            energy_prices=self.energy_prices,
            industrial_capex=self.industrial_capex,
            emerging_market_growth=self.emerging_market_growth,
            healthcare_spending=self.healthcare_spending,
            financial_conditions=self.financial_conditions,
            usd_strength=self.usd_strength,
            interest_rate_sensitivity=self.interest_rate_sensitivity,
            profile_source=self.profile_source,
        )

    def revenue_profile(self) -> dict[str, float]:
        return {bucket: float(getattr(self, column_name)) for bucket, column_name in REVENUE_COLUMNS.items()}

    def dependency_profile(self) -> dict[str, float]:
        return {dependency_name: float(getattr(self, dependency_name)) for dependency_name in DEPENDENCY_COLUMNS}


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
                country_code=record.country_code,
                revenue_us=record.revenue_us,
                revenue_europe=record.revenue_europe,
                revenue_china=record.revenue_china,
                revenue_apac_ex_china=record.revenue_apac_ex_china,
                revenue_japan=record.revenue_japan,
                revenue_latam=record.revenue_latam,
                revenue_mea=record.revenue_mea,
                revenue_other=record.revenue_other,
                us_consumer=record.us_consumer,
                china_demand=record.china_demand,
                europe_demand=record.europe_demand,
                ai_capex=record.ai_capex,
                cloud_spending=record.cloud_spending,
                global_semiconductors=record.global_semiconductors,
                energy_prices=record.energy_prices,
                industrial_capex=record.industrial_capex,
                emerging_market_growth=record.emerging_market_growth,
                healthcare_spending=record.healthcare_spending,
                financial_conditions=record.financial_conditions,
                usd_strength=record.usd_strength,
                interest_rate_sensitivity=record.interest_rate_sensitivity,
                profile_source=record.profile_source,
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
class MacroScenario:
    name: str
    display_name: str
    description: str
    shock_weights: dict[str, float]

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        self.display_name = self.display_name.strip()
        self.description = self.description.strip()
        if not self.name:
            raise ValidationError("Scenario name cannot be empty.")
        unknown = set(self.shock_weights) - set(DEPENDENCY_COLUMNS)
        if unknown:
            raise ValidationError(f"Unknown dependency names in scenario {self.name}: {sorted(unknown)}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "shock_weights": self.shock_weights,
        }


@dataclass
class DependencyAnalysisResult:
    normalized_portfolio_weights: list[dict[str, Any]]
    underlying_company_exposures: list[dict[str, Any]]
    country_exposure_table: list[dict[str, Any]]
    region_exposure_table: list[dict[str, Any]]
    currency_exposure_table: list[dict[str, Any]]
    sector_exposure_table: list[dict[str, Any]]
    revenue_geography_exposure_table: list[dict[str, Any]]
    macro_dependency_exposure_table: list[dict[str, Any]]
    concentration_metrics: dict[str, Any]
    diversification_scores: dict[str, float]
    domicile_vs_revenue_comparison: list[dict[str, Any]]
    scenario_impact_results: list[dict[str, Any]]
    warnings: list[str]
    summary_insights: list[str]
    recommendations: list[str]
    heatmap_ready_data: list[dict[str, Any]]
    map_ready_data: list[dict[str, Any]]
    network_graph_data: dict[str, Any]
    viral_summary_card: dict[str, Any]
    sector_region_matrix: list[dict[str, Any]]
    analysis_metadata: dict[str, Any] = field(
        default_factory=lambda: {"generated_at": datetime.now(timezone.utc).isoformat()}
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

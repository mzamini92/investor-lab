from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, PositiveFloat


class PortfolioPosition(BaseModel):
    ticker: str = Field(..., min_length=1)
    quantity: PositiveFloat
    price: PositiveFloat


class HoldingExposure(BaseModel):
    ticker: str
    market_value: float
    portfolio_weight: float
    us_exposure_pct: float
    international_exposure_pct: float
    asset_class: str
    geography_label: str


class PortfolioExposureSummary(BaseModel):
    total_market_value: float
    portfolio_us_weight: float
    portfolio_international_weight: float
    home_bias_level: str
    holdings: list[HoldingExposure]


class ValuationGap(BaseModel):
    as_of: str
    us_forward_pe: float
    international_forward_pe: float
    valuation_spread_ratio: float
    us_premium_pct: float
    international_discount_pct: float
    spread_percentile_vs_history: float
    narrative: str


class DollarCycle(BaseModel):
    as_of: str
    dxy: float
    reer: float
    dxy_percentile_10y: float
    dxy_trend: str
    regime: Literal["STRONG_DOLLAR", "PEAK_DOLLAR", "WEAKENING_DOLLAR", "WEAK_DOLLAR"]
    narrative: str


class EarningsGrowthGap(BaseModel):
    as_of: str
    us_earnings_growth_pct: float
    international_earnings_growth_pct: float
    earnings_growth_gap_pct_points: float
    narrative: str


class HistoricalAnalog(BaseModel):
    date: str
    us_forward_pe: float
    international_forward_pe: float
    valuation_spread_ratio: float
    following_5y_intl_minus_us_ann_pct: float
    similarity_score: float


class HistoricalAnalogSummary(BaseModel):
    average_following_5y_outperformance_pct: float
    analog_count: int
    analogs: list[HistoricalAnalog]
    narrative: str


class SimulationPortfolioMetrics(BaseModel):
    label: str
    us_weight: float
    international_weight: float
    expected_annual_return_pct: float
    annualized_volatility_pct: float
    sharpe_ratio: float


class DiversificationAdjustment(BaseModel):
    current_international_weight: float
    suggested_international_weight: float
    suggested_us_weight: float
    suggested_vehicle_examples: list[str]
    rationale: str


class SimulationSummary(BaseModel):
    current_portfolio: SimulationPortfolioMetrics
    diversified_portfolio: SimulationPortfolioMetrics
    sharpe_ratio_change: float
    expected_return_change_pct: float
    volatility_change_pct: float
    narrative: str


class RecommendationSummary(BaseModel):
    headline: str
    plain_english_note: str
    suggested_adjustment: DiversificationAdjustment
    diversification_benefit_note: str


class VisualizationData(BaseModel):
    exposure_pie: list[dict[str, Any]]
    valuation_history: list[dict[str, Any]]
    dollar_history: list[dict[str, Any]]
    analog_bars: list[dict[str, Any]]
    simulation_bars: list[dict[str, Any]]


class GlobalGapAnalysis(BaseModel):
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    portfolio_exposure: PortfolioExposureSummary
    valuation_gap: ValuationGap
    earnings_growth_gap: EarningsGrowthGap
    dollar_cycle: DollarCycle
    historical_analogs: HistoricalAnalogSummary
    simulation: SimulationSummary
    recommendation: RecommendationSummary
    visualization_data: VisualizationData


class MacroDataSnapshot(BaseModel):
    valuation_gap: ValuationGap
    earnings_growth_gap: EarningsGrowthGap
    dollar_cycle: DollarCycle

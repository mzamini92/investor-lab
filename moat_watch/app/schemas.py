from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class WatchlistItemRequest(BaseModel):
    ticker: str = Field(..., min_length=1)
    purchase_thesis_notes: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    benchmark_peers: Optional[list[str]] = None
    company_category: Optional[str] = None
    historical_baseline_quarter: Optional[str] = None


class QuarterlyMetricsRequest(BaseModel):
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


class CommentaryRequest(BaseModel):
    ticker: str
    quarter: str
    raw_commentary_text: str = ""
    mentions_pricing_pressure: bool = False
    mentions_competition: bool = False
    mentions_promotions: bool = False
    mentions_market_share_gain: bool = False
    mentions_market_share_loss: bool = False
    mentions_customer_weakness: bool = False
    mentions_cost_pressure: bool = False
    mentions_innovation_strength: bool = False


class AnalyzeCompanyMoatRequest(BaseModel):
    ticker: Optional[str] = None
    quarter: Optional[str] = None
    current_metrics: Optional[QuarterlyMetricsRequest] = None
    prior_quarter: Optional[QuarterlyMetricsRequest] = None
    prior_year_quarter: Optional[QuarterlyMetricsRequest] = None
    peer_data: Optional[list[QuarterlyMetricsRequest]] = None
    commentary: Optional[CommentaryRequest] = None


class AnalyzeWatchlistQuarterRequest(BaseModel):
    watchlist: list[WatchlistItemRequest]
    quarter: str

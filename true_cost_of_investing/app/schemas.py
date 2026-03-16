from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, PositiveFloat


class HoldingInputRequest(BaseModel):
    ticker: str = Field(..., min_length=1)
    amount: PositiveFloat
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


class PortfolioAssumptionsRequest(BaseModel):
    monthly_contribution: float = 0.0
    annual_gross_return: float
    investment_horizon_years: int = Field(..., gt=0)
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


class AnalyzePortfolioCostRequest(BaseModel):
    holdings: list[HoldingInputRequest]
    assumptions: PortfolioAssumptionsRequest


class ComparePortfoliosRequest(BaseModel):
    current_portfolio: list[HoldingInputRequest]
    alternative_portfolio: list[HoldingInputRequest]
    assumptions: PortfolioAssumptionsRequest

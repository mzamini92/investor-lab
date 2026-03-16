from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class AccountRequest(BaseModel):
    account_id: str
    account_name: str
    account_type: str
    taxable_flag: bool
    owner_id: Optional[str] = None


class PositionRequest(BaseModel):
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


class TaxLotRequest(BaseModel):
    account_id: str
    ticker: str
    lot_id: str
    acquisition_date: str
    quantity: float
    cost_basis_per_share: float
    total_cost_basis: Optional[float] = None
    current_price: float
    unrealized_gain_loss: Optional[float] = None
    short_term_or_long_term: Optional[str] = None


class TransactionRequest(BaseModel):
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


class TaxAssumptionsRequest(BaseModel):
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


class ReplacementSecurityRequest(BaseModel):
    ticker: str
    security_name: str
    asset_class: str
    region: str
    market_cap_focus: str
    style: str
    factor_tilt: Optional[str] = None
    sector_focus: Optional[str] = None
    expense_ratio: float
    benchmark_index: str
    strategy_tags: list[str]
    similar_to: list[str] = []
    prohibited_as_replacement_for: list[str] = []
    holdings_similarity_score: Optional[float] = None


class ScanHarvestRequest(BaseModel):
    accounts: list[AccountRequest]
    positions: list[PositionRequest]
    lots: list[TaxLotRequest]
    transactions: list[TransactionRequest]
    tax_assumptions: TaxAssumptionsRequest
    replacement_universe: list[ReplacementSecurityRequest]
    scan_date: Optional[str] = None


class EvaluateSinglePositionRequest(BaseModel):
    position: PositionRequest
    lots: list[TaxLotRequest] = []
    transactions: list[TransactionRequest] = []
    tax_assumptions: TaxAssumptionsRequest
    replacement_universe: list[ReplacementSecurityRequest]
    account: Optional[AccountRequest] = None
    scan_date: Optional[str] = None

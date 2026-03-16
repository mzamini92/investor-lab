from __future__ import annotations

from harvest_alert.app.models import Position, TaxAssumptions, TaxLot


def applicable_tax_rate(term: str, assumptions: TaxAssumptions) -> float:
    if term == "short_term":
        return assumptions.effective_short_term_rate
    if term == "long_term":
        return assumptions.effective_long_term_rate
    return assumptions.default_loss_benefit_rate + assumptions.state_tax_rate


def estimate_tax_savings(harvestable_loss: float, rate: float) -> float:
    return round(harvestable_loss * rate, 2)


def estimate_trading_cost(market_value: float, assumptions: TaxAssumptions) -> float:
    total_bps = assumptions.trading_cost_bps + assumptions.bid_ask_cost_bps + assumptions.slippage_bps
    return round(market_value * total_bps / 10000.0, 2)


def estimate_lot_benefit(lot: TaxLot, assumptions: TaxAssumptions) -> dict[str, float]:
    harvestable_loss = max(0.0, -(lot.unrealized_gain_loss or 0.0))
    tax_rate = applicable_tax_rate(lot.short_term_or_long_term or "unknown", assumptions)
    estimated_tax = estimate_tax_savings(harvestable_loss, tax_rate)
    market_value = lot.current_price * lot.quantity
    trading_cost = estimate_trading_cost(market_value, assumptions)
    return {
        "harvestable_loss": round(harvestable_loss, 2),
        "tax_rate_used": round(tax_rate, 6),
        "estimated_tax_savings": estimated_tax,
        "transaction_cost_estimate": trading_cost,
        "net_estimated_benefit": round(estimated_tax - trading_cost, 2),
        "loss_pct_from_basis": round(harvestable_loss / (lot.total_cost_basis or 1.0), 6) if lot.total_cost_basis else 0.0,
    }


def estimate_position_level_benefit(position: Position, assumptions: TaxAssumptions) -> dict[str, float]:
    harvestable_loss = max(0.0, -(position.unrealized_gain_loss or 0.0))
    tax_rate = assumptions.default_loss_benefit_rate + assumptions.state_tax_rate
    estimated_tax = estimate_tax_savings(harvestable_loss, tax_rate)
    trading_cost = estimate_trading_cost(position.market_value, assumptions)
    return {
        "harvestable_loss": round(harvestable_loss, 2),
        "tax_rate_used": round(tax_rate, 6),
        "estimated_tax_savings": estimated_tax,
        "transaction_cost_estimate": trading_cost,
        "net_estimated_benefit": round(estimated_tax - trading_cost, 2),
        "loss_pct_from_basis": round(harvestable_loss / (position.cost_basis_total or 1.0), 6) if position.cost_basis_total else 0.0,
    }

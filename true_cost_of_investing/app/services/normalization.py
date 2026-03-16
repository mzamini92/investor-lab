from __future__ import annotations

from typing import Any

from true_cost_of_investing.app.models import HoldingInput, NormalizedHolding


def normalize_holdings(holdings: list[HoldingInput]) -> tuple[list[NormalizedHolding], dict[str, Any]]:
    total_value = sum(holding.amount for holding in holdings)
    if total_value <= 0:
        raise ValueError("Portfolio total value must be positive.")

    normalized = [
        NormalizedHolding(
            ticker=holding.ticker,
            amount=holding.amount,
            weight=holding.amount / total_value,
            expense_ratio=holding.expense_ratio,
            asset_type=holding.asset_type,
            dividend_yield=holding.dividend_yield,
            qualified_dividend_yield=holding.qualified_dividend_yield,
            nonqualified_dividend_yield=holding.nonqualified_dividend_yield,
            annual_turnover_rate=holding.annual_turnover_rate,
            estimated_spread_cost_bps=holding.estimated_spread_cost_bps,
            advisory_fee_override=holding.advisory_fee_override,
            withholding_tax_rate=holding.withholding_tax_rate or 0.0,
            layered_fee_ratio=holding.layered_fee_ratio,
        )
        for holding in holdings
    ]

    metrics = {
        "portfolio_value": round(total_value, 2),
        "blended_expense_ratio": sum(row.weight * row.expense_ratio for row in normalized),
        "blended_dividend_yield": sum(row.weight * row.dividend_yield for row in normalized),
        "blended_qualified_dividend_yield": sum(row.weight * row.qualified_dividend_yield for row in normalized),
        "blended_nonqualified_dividend_yield": sum(row.weight * row.nonqualified_dividend_yield for row in normalized),
        "blended_turnover_rate": sum(row.weight * row.annual_turnover_rate for row in normalized),
        "blended_spread_cost_bps": sum(row.weight * row.estimated_spread_cost_bps for row in normalized),
        "blended_withholding_tax_rate": sum(row.weight * row.withholding_tax_rate for row in normalized),
        "blended_layered_fee_ratio": sum(row.weight * row.layered_fee_ratio for row in normalized),
    }
    return normalized, metrics

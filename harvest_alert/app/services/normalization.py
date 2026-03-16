from __future__ import annotations

from typing import Any

from harvest_alert.app.models import Account, Position, TaxLot, Transaction
from harvest_alert.app.utils.dates import days_between


def normalize_brokerage_data(
    *,
    accounts: list[Account],
    positions: list[Position],
    lots: list[TaxLot],
    transactions: list[Transaction],
    scan_date: str,
) -> dict[str, Any]:
    account_map = {account.account_id: account for account in accounts}
    taxable_accounts = {account.account_id for account in accounts if account.taxable_flag}

    normalized_positions: list[Position] = []
    for position in positions:
        if position.cost_basis_total is None:
            linked_lots = [lot for lot in lots if lot.account_id == position.account_id and lot.ticker == position.ticker]
            if linked_lots:
                position.cost_basis_total = round(sum((lot.total_cost_basis or (lot.cost_basis_per_share * lot.quantity)) for lot in linked_lots), 2)
        if position.unrealized_gain_loss is None and position.cost_basis_total is not None:
            position.unrealized_gain_loss = round(position.market_value - position.cost_basis_total, 2)
        normalized_positions.append(position)

    normalized_lots: list[TaxLot] = []
    for lot in lots:
        if lot.total_cost_basis is None:
            lot.total_cost_basis = round(lot.cost_basis_per_share * lot.quantity, 2)
        if lot.unrealized_gain_loss is None:
            lot.unrealized_gain_loss = round((lot.current_price - lot.cost_basis_per_share) * lot.quantity, 2)
        if lot.short_term_or_long_term is None:
            lot.short_term_or_long_term = "long_term" if days_between(scan_date, lot.acquisition_date) >= 365 else "short_term"
        normalized_lots.append(lot)

    data_flags: list[str] = []
    if not transactions:
        data_flags.append("No transaction history supplied; wash-sale screening confidence is lower.")
    if not any(account.account_type in {"ira", "roth_ira"} for account in accounts):
        data_flags.append("No IRA accounts supplied; cross-account wash-sale visibility may be incomplete.")

    return {
        "account_map": account_map,
        "taxable_accounts": taxable_accounts,
        "positions": normalized_positions,
        "lots": normalized_lots,
        "transactions": transactions,
        "data_completeness_flags": data_flags,
    }

from __future__ import annotations

from typing import Any

from harvest_alert.app.models import Account, ReplacementSecurity, Transaction
from harvest_alert.app.utils.dates import days_between


def screen_wash_sale_conflicts(
    *,
    ticker: str,
    proposed_sale_date: str,
    transactions: list[Transaction],
    accounts: dict[str, Account],
    replacement: ReplacementSecurity | None = None,
) -> dict[str, Any]:
    conflict_transactions: list[dict[str, Any]] = []
    conflict_accounts: list[str] = []
    risk_level = "none"
    explanations: list[str] = []

    for transaction in transactions:
        if transaction.ticker != ticker:
            continue
        if transaction.side.lower() != "buy":
            continue
        delta = abs(days_between(proposed_sale_date, transaction.trade_date))
        if delta <= 30:
            account = accounts.get(transaction.account_id)
            conflict_transactions.append(
                {
                    "account_id": transaction.account_id,
                    "trade_date": transaction.trade_date,
                    "ticker": transaction.ticker,
                    "transaction_type": transaction.transaction_type,
                    "side": transaction.side,
                    "recurring_flag": transaction.recurring_flag,
                }
            )
            conflict_accounts.append(transaction.account_id)
            if account and account.account_type in {"ira", "roth_ira"}:
                risk_level = "high"
                explanations.append(f"Recent identical-ticker buy in {account.account_type} account {transaction.account_id}.")
            elif transaction.recurring_flag:
                risk_level = "medium" if risk_level != "high" else risk_level
                explanations.append(f"Recurring buy detected for {ticker} within the wash-sale window.")
            else:
                risk_level = "medium" if risk_level not in {"high"} else risk_level
                explanations.append(f"Recent identical-ticker buy detected in account {transaction.account_id}.")

    if replacement is not None:
        if replacement.ticker == ticker:
            risk_level = "high"
            explanations.append("Exact same ticker replacement is prohibited.")
        elif ticker in replacement.prohibited_as_replacement_for:
            risk_level = "high"
            explanations.append(f"{replacement.ticker} is explicitly marked as a prohibited replacement for {ticker}.")
        elif replacement.holdings_similarity_score is not None and replacement.holdings_similarity_score >= 0.98:
            if risk_level not in {"high"}:
                risk_level = "low"
            explanations.append("Replacement looks extremely close on holdings overlap; manual wash-sale review is prudent.")

    unique_explanations = list(dict.fromkeys(explanations))
    summary = "none detected" if not unique_explanations else " ".join(unique_explanations)
    return {
        "wash_sale_risk_level": risk_level,
        "conflict_transactions": conflict_transactions,
        "conflict_accounts": sorted(set(conflict_accounts)),
        "explanation": summary,
    }

from __future__ import annotations

from harvest_alert.app.models import Account, Position, ReplacementSecurity, TaxAssumptions, TaxLot, Transaction
from harvest_alert.app.providers.base import BrokerageDataProvider


class MockBrokerageProvider(BrokerageDataProvider):
    def __init__(
        self,
        *,
        accounts: list[Account],
        positions: list[Position],
        lots: list[TaxLot],
        transactions: list[Transaction],
        tax_assumptions: TaxAssumptions,
        replacements: list[ReplacementSecurity],
    ) -> None:
        self._accounts = accounts
        self._positions = positions
        self._lots = lots
        self._transactions = transactions
        self._tax_assumptions = tax_assumptions
        self._replacements = replacements

    def get_accounts(self) -> list[Account]:
        return self._accounts

    def get_positions(self) -> list[Position]:
        return self._positions

    def get_lots(self) -> list[TaxLot]:
        return self._lots

    def get_transactions(self) -> list[Transaction]:
        return self._transactions

    def get_tax_assumptions(self) -> TaxAssumptions:
        return self._tax_assumptions

    def get_replacements(self) -> list[ReplacementSecurity]:
        return self._replacements

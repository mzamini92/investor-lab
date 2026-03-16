from __future__ import annotations

import json

from harvest_alert.app.config import (
    ACCOUNTS_FILE,
    LOTS_FILE,
    POSITIONS_FILE,
    REPLACEMENTS_FILE,
    TAX_ASSUMPTIONS_FILE,
    TRANSACTIONS_FILE,
)
from harvest_alert.app.models import Account, Position, ReplacementSecurity, TaxAssumptions, TaxLot, Transaction
from harvest_alert.app.providers.base import BrokerageDataProvider


class LocalBrokerageProvider(BrokerageDataProvider):
    def get_accounts(self) -> list[Account]:
        return [Account(**item) for item in json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))]

    def get_positions(self) -> list[Position]:
        return [Position(**item) for item in json.loads(POSITIONS_FILE.read_text(encoding="utf-8"))]

    def get_lots(self) -> list[TaxLot]:
        return [TaxLot(**item) for item in json.loads(LOTS_FILE.read_text(encoding="utf-8"))]

    def get_transactions(self) -> list[Transaction]:
        return [Transaction(**item) for item in json.loads(TRANSACTIONS_FILE.read_text(encoding="utf-8"))]

    def get_tax_assumptions(self) -> TaxAssumptions:
        return TaxAssumptions(**json.loads(TAX_ASSUMPTIONS_FILE.read_text(encoding="utf-8")))

    def get_replacements(self) -> list[ReplacementSecurity]:
        return [ReplacementSecurity(**item) for item in json.loads(REPLACEMENTS_FILE.read_text(encoding="utf-8"))]

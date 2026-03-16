from __future__ import annotations

from abc import ABC, abstractmethod

from harvest_alert.app.models import Account, Position, ReplacementSecurity, TaxAssumptions, TaxLot, Transaction


class BrokerageDataProvider(ABC):
    @abstractmethod
    def get_accounts(self) -> list[Account]:
        raise NotImplementedError

    @abstractmethod
    def get_positions(self) -> list[Position]:
        raise NotImplementedError

    @abstractmethod
    def get_lots(self) -> list[TaxLot]:
        raise NotImplementedError

    @abstractmethod
    def get_transactions(self) -> list[Transaction]:
        raise NotImplementedError

    @abstractmethod
    def get_tax_assumptions(self) -> TaxAssumptions:
        raise NotImplementedError

    @abstractmethod
    def get_replacements(self) -> list[ReplacementSecurity]:
        raise NotImplementedError

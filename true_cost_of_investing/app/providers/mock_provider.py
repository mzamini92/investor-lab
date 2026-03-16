from __future__ import annotations

from true_cost_of_investing.app.models import HoldingInput, PortfolioAssumptions


class MockPortfolioProvider:
    def __init__(self, holdings: list[HoldingInput], assumptions: PortfolioAssumptions) -> None:
        self.holdings = holdings
        self.assumptions = assumptions

    def load_portfolio(self) -> list[HoldingInput]:
        return self.holdings

    def load_assumptions(self) -> PortfolioAssumptions:
        return self.assumptions

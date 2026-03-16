from __future__ import annotations

import json
from pathlib import Path

from true_cost_of_investing.app.models import PortfolioAssumptions
from true_cost_of_investing.app.providers.base import DataProvider


class AssumptionsProvider(DataProvider):
    def load(self, path: Path) -> PortfolioAssumptions:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Assumptions file must contain a JSON object.")
        return PortfolioAssumptions(**payload)

from __future__ import annotations

import json
from pathlib import Path

from true_cost_of_investing.app.models import HoldingInput
from true_cost_of_investing.app.providers.base import DataProvider


class PortfolioProvider(DataProvider):
    def load(self, path: Path) -> list[HoldingInput]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("Portfolio file must contain a JSON list.")
        return [HoldingInput(**item) for item in payload]

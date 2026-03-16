from __future__ import annotations

import json
from pathlib import Path

from earnings_clarity.app.config import EARNINGS_DIR
from earnings_clarity.app.exceptions import EarningsEventNotFoundError
from earnings_clarity.app.models import EarningsEvent
from earnings_clarity.app.providers.base import EarningsEventProvider


class LocalEarningsEventProvider(EarningsEventProvider):
    def __init__(self, earnings_dir: Path = EARNINGS_DIR) -> None:
        self.earnings_dir = Path(earnings_dir)

    def get_earnings_event(self, ticker: str, quarter: str) -> EarningsEvent:
        path = self.earnings_dir / f"{ticker.upper()}_{quarter}.json"
        if not path.exists():
            raise EarningsEventNotFoundError(f"Earnings event not found for {ticker.upper()} {quarter}.")
        return EarningsEvent(**json.loads(path.read_text(encoding="utf-8")))

    def list_events(self) -> list[EarningsEvent]:
        return [
            EarningsEvent(**json.loads(path.read_text(encoding="utf-8")))
            for path in sorted(self.earnings_dir.glob("*.json"))
        ]

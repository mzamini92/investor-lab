from __future__ import annotations

import pandas as pd

from economic_regime_translator.app.models import MacroSnapshot


class MockMacroProvider:
    def __init__(self, current: MacroSnapshot, history: pd.DataFrame) -> None:
        self.current = current
        self.history = history

    def load_snapshot(self) -> MacroSnapshot:
        return self.current

    def load_history(self) -> pd.DataFrame:
        return self.history

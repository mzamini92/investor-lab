from __future__ import annotations

from pathlib import Path

import pandas as pd

from economic_regime_translator.app.providers.base import DataProvider


class HistoryProvider(DataProvider):
    def load(self, path: Path) -> pd.DataFrame:
        df = pd.read_csv(path)
        if "observation_date" not in df.columns:
            raise ValueError("Historical dataset must include observation_date.")
        return df

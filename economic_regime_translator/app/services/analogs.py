from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from economic_regime_translator.app.config import DEFAULT_ANALOG_FIELDS
from economic_regime_translator.app.models import MacroSnapshot
from economic_regime_translator.app.utils.constants import ASSET_COLUMNS


def find_historical_analogs(
    current_snapshot: MacroSnapshot,
    history_df: pd.DataFrame,
    *,
    top_n: int = 5,
) -> list[dict[str, Any]]:
    if history_df.empty:
        return []

    analog_fields = [field for field in DEFAULT_ANALOG_FIELDS if field in history_df.columns]
    history_numeric = history_df[analog_fields].astype(float)
    means = history_numeric.mean()
    stds = history_numeric.std().replace(0.0, 1.0)
    normalized_history = (history_numeric - means) / stds
    current_vector = np.array([(float(getattr(current_snapshot, field)) - means[field]) / stds[field] for field in analog_fields])

    distances = np.sqrt(((normalized_history - current_vector) ** 2).sum(axis=1))
    ranked = history_df.copy()
    ranked["distance"] = distances
    ranked["similarity_score"] = 1.0 / (1.0 + ranked["distance"])
    ranked = ranked.sort_values("distance").head(top_n)

    analogs: list[dict[str, Any]] = []
    for _, row in ranked.iterrows():
        asset_behavior = {column: float(row[column]) for column in ASSET_COLUMNS if column in row and not pd.isna(row[column])}
        analogs.append(
            {
                "observation_date": str(row["observation_date"]),
                "similarity_score": round(float(row["similarity_score"]), 6),
                "regime_label": str(row.get("regime_label", "Unlabeled historical analog")),
                "summary": str(row.get("summary", "")),
                "asset_behavior": asset_behavior,
            }
        )
    return analogs

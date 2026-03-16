from __future__ import annotations

from typing import Any

import pandas as pd

from hedgefund_dependency_engine.app.config import DEPENDENCY_COLUMNS


def aggregate_dependency_exposures(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for dependency_name, metadata in DEPENDENCY_COLUMNS.items():
        exposure = float((frame["company_exposure"] * frame[dependency_name]).sum())
        rows.append(
            {
                "dependency_name": dependency_name,
                "display_name": metadata["display_name"],
                "category_group": metadata["category_group"],
                "exposure": exposure,
                "exposure_pct": exposure * 100.0,
            }
        )
    return pd.DataFrame(rows).sort_values(["exposure", "display_name"], ascending=[False, True]).reset_index(drop=True)


def build_heatmap_ready_data(dependency_exposure_df: pd.DataFrame) -> pd.DataFrame:
    df = dependency_exposure_df.copy()
    max_exposure = float(df["exposure"].max()) if not df.empty else 0.0
    df["intensity_score"] = 0.0 if max_exposure <= 0 else (df["exposure"] / max_exposure) * 100.0
    return df[["dependency_name", "display_name", "exposure_pct", "category_group", "intensity_score"]]

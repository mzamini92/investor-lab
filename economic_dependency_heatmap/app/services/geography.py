from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def add_country_code(country_exposure_df: pd.DataFrame, underlying_exposures_df: pd.DataFrame) -> pd.DataFrame:
    country_codes = (
        underlying_exposures_df.groupby("country_domicile", dropna=False)
        .agg(country_code=("country_code", "first"))
        .reset_index()
        .rename(columns={"country_domicile": "name"})
    )
    return country_exposure_df.merge(country_codes, on="name", how="left")


def compute_distribution_metrics(exposure_df: pd.DataFrame, top_n: tuple[int, ...] = (3, 5)) -> dict[str, Any]:
    exposures = exposure_df["exposure"].to_numpy(dtype=float)
    hhi = float(np.square(exposures).sum()) if len(exposures) else 0.0
    effective_count = float(1.0 / hhi) if hhi > 0 else 0.0
    metrics: dict[str, Any] = {
        "count": int(len(exposure_df)),
        "hhi": round(hhi, 6),
        "effective_count": round(effective_count, 6),
        "top_concentration": round(float(exposures[:1].sum()), 6),
    }
    for n in top_n:
        metrics[f"top_{n}_concentration"] = round(float(exposures[:n].sum()), 6)
    return metrics

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


def compute_concentration_metrics(exposure_df: pd.DataFrame, top_n: int) -> dict[str, Any]:
    exposures = exposure_df["exposure"].to_numpy(dtype=float)
    hhi = float(np.square(exposures).sum()) if len(exposures) else 0.0
    effective_number = float(1.0 / hhi) if hhi > 0 else 0.0
    return {
        f"top_{top_n}_concentration": round(float(exposures[:top_n].sum()), 6),
        "hhi": round(hhi, 6),
        "effective_count": round(effective_number, 6),
    }


def compute_country_metrics(country_exposure_df: pd.DataFrame) -> dict[str, Any]:
    base = compute_concentration_metrics(country_exposure_df, top_n=3)
    top_5 = round(float(country_exposure_df["exposure"].head(5).sum()), 6)
    base["top_5_concentration"] = top_5
    return base


def compute_region_metrics(region_exposure_df: pd.DataFrame) -> dict[str, Any]:
    top_region = region_exposure_df.iloc[0] if not region_exposure_df.empty else None
    base = compute_concentration_metrics(region_exposure_df, top_n=1)
    base["top_region_concentration"] = base.pop("top_1_concentration")
    if top_region is not None:
        base["top_region"] = str(top_region["name"])
        base["top_region_exposure"] = round(float(top_region["exposure"]), 6)
    else:
        base["top_region"] = ""
        base["top_region_exposure"] = 0.0
    return base

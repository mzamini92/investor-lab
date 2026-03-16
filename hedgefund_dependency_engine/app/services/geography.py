from __future__ import annotations

import pandas as pd


def add_country_code(country_exposure_df: pd.DataFrame, underlying_exposure_df: pd.DataFrame) -> pd.DataFrame:
    codes = (
        underlying_exposure_df.groupby("country_domicile", dropna=False)
        .agg(country_code=("country_code", "first"))
        .reset_index()
        .rename(columns={"country_domicile": "name"})
    )
    return country_exposure_df.merge(codes, on="name", how="left")

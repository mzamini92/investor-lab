from __future__ import annotations

from typing import Any

import pandas as pd


REVENUE_COLUMNS = {
    "North America": "revenue_north_america",
    "Europe": "revenue_europe",
    "Asia Pacific": "revenue_asia_pacific",
    "Emerging Markets": "revenue_emerging_markets",
    "Latin America": "revenue_latin_america",
    "Middle East & Africa": "revenue_middle_east_africa",
}


def aggregate_underlying_company_exposures(constituent_frame: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        constituent_frame.groupby("underlying_ticker", dropna=False)
        .agg(
            company_name=("company_name", "first"),
            exposure=("exposure", "sum"),
            sector=("sector", "first"),
            country_domicile=("country_domicile", "first"),
            region=("region", "first"),
            currency=("currency", "first"),
            market_cap_bucket=("market_cap_bucket", "first"),
            country_code=("country_code", "first"),
            contributing_etfs=("etf_ticker", lambda values: sorted(set(values))),
        )
        .reset_index()
        .sort_values(["exposure", "underlying_ticker"], ascending=[False, True])
        .reset_index(drop=True)
    )
    grouped["contributing_etf_count"] = grouped["contributing_etfs"].apply(len)
    grouped["exposure_pct"] = grouped["exposure"] * 100.0
    return grouped


def aggregate_dimension_exposure(constituent_frame: pd.DataFrame, dimension: str) -> pd.DataFrame:
    grouped = (
        constituent_frame.groupby(dimension, dropna=False)
        .agg(exposure=("exposure", "sum"))
        .reset_index()
        .rename(columns={dimension: "name"})
        .sort_values(["exposure", "name"], ascending=[False, True])
        .reset_index(drop=True)
    )
    grouped["exposure_pct"] = grouped["exposure"] * 100.0
    return grouped


def aggregate_region_revenue_exposure(constituent_frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for region_name, column_name in REVENUE_COLUMNS.items():
        value = float((constituent_frame["exposure"] * constituent_frame[column_name]).sum())
        rows.append({"name": region_name, "exposure": value, "exposure_pct": value * 100.0})
    return pd.DataFrame(rows).sort_values(["exposure", "name"], ascending=[False, True]).reset_index(drop=True)


def build_domicile_vs_revenue(region_exposure_df: pd.DataFrame, revenue_exposure_df: pd.DataFrame) -> pd.DataFrame:
    domicile = region_exposure_df.rename(columns={"exposure": "domicile_exposure", "exposure_pct": "domicile_exposure_pct"})
    revenue = revenue_exposure_df.rename(columns={"exposure": "revenue_exposure", "exposure_pct": "revenue_exposure_pct"})
    merged = domicile.merge(revenue, on="name", how="outer").fillna(0.0)
    merged["absolute_gap"] = (merged["domicile_exposure"] - merged["revenue_exposure"]).abs()
    merged["absolute_gap_pct"] = merged["absolute_gap"] * 100.0
    return merged.sort_values(["domicile_exposure", "name"], ascending=[False, True]).reset_index(drop=True)


def build_sector_region_matrix(constituent_frame: pd.DataFrame) -> pd.DataFrame:
    matrix = (
        constituent_frame.pivot_table(
            index="sector",
            columns="region",
            values="exposure",
            aggfunc="sum",
            fill_value=0.0,
        )
        .reset_index()
    )
    return matrix


def build_map_ready_data(country_exposure_df: pd.DataFrame) -> pd.DataFrame:
    df = country_exposure_df.rename(
        columns={
            "name": "country_name",
            "country_code": "country_code",
            "exposure_pct": "portfolio_exposure_pct",
        }
    )
    expected_columns = ["country_code", "country_name", "portfolio_exposure_pct", "exposure"]
    for column in expected_columns:
        if column not in df.columns:
            df[column] = 0.0 if column != "country_name" else ""
    return df[["country_code", "country_name", "portfolio_exposure_pct", "exposure"]]


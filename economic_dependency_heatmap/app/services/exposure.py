from __future__ import annotations

from typing import Any

import pandas as pd

from economic_dependency_heatmap.app.config import REVENUE_COLUMNS


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
            profile_source=("profile_source", "first"),
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


def aggregate_revenue_geography_exposure(constituent_frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for bucket, column_name in REVENUE_COLUMNS.items():
        exposure = float((constituent_frame["exposure"] * constituent_frame[column_name]).sum())
        rows.append({"name": bucket, "exposure": exposure, "exposure_pct": exposure * 100.0})
    return pd.DataFrame(rows).sort_values(["exposure", "name"], ascending=[False, True]).reset_index(drop=True)


def domicile_bucket_for_row(row: pd.Series) -> str:
    country = str(row["country_domicile"])
    region = str(row["region"])
    if country == "United States":
        return "United States"
    if country == "China":
        return "China"
    if country == "Japan":
        return "Japan"
    if region == "Europe":
        return "Europe"
    if region == "Latin America":
        return "Latin America"
    if region == "Middle East & Africa":
        return "Middle East & Africa"
    if region == "Asia Pacific":
        return "APAC ex-China"
    return "Other"


def aggregate_domicile_buckets(constituent_frame: pd.DataFrame) -> pd.DataFrame:
    df = constituent_frame.copy()
    df["domicile_bucket"] = df.apply(domicile_bucket_for_row, axis=1)
    return aggregate_dimension_exposure(df, "domicile_bucket")


def build_domicile_vs_revenue(domicile_bucket_df: pd.DataFrame, revenue_exposure_df: pd.DataFrame) -> pd.DataFrame:
    domicile = domicile_bucket_df.rename(columns={"exposure": "domicile_exposure", "exposure_pct": "domicile_exposure_pct"})
    revenue = revenue_exposure_df.rename(columns={"exposure": "revenue_exposure", "exposure_pct": "revenue_exposure_pct"})
    merged = domicile.merge(revenue, on="name", how="outer").fillna(0.0)
    merged["absolute_gap"] = (merged["domicile_exposure"] - merged["revenue_exposure"]).abs()
    merged["absolute_gap_pct"] = merged["absolute_gap"] * 100.0
    return merged.sort_values(["absolute_gap", "name"], ascending=[False, True]).reset_index(drop=True)


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


def build_map_ready_data(country_exposure_df: pd.DataFrame, revenue_exposure_df: pd.DataFrame) -> pd.DataFrame:
    revenue_lookup = {
        "United States": float(revenue_exposure_df.loc[revenue_exposure_df["name"] == "United States", "exposure_pct"].sum()),
        "China": float(revenue_exposure_df.loc[revenue_exposure_df["name"] == "China", "exposure_pct"].sum()),
        "Japan": float(revenue_exposure_df.loc[revenue_exposure_df["name"] == "Japan", "exposure_pct"].sum()),
    }
    df = country_exposure_df.copy()
    df["domicile_exposure_pct"] = df["exposure"] * 100.0
    df["revenue_exposure_pct"] = df["name"].map(revenue_lookup).fillna(0.0)
    df["dependency_relevance_note"] = df["name"].apply(
        lambda country_name: "Direct revenue bucket available" if country_name in revenue_lookup else "Revenue tracked at regional level"
    )
    return df.rename(columns={"name": "country_name"})[
        ["country_code", "country_name", "domicile_exposure_pct", "revenue_exposure_pct", "dependency_relevance_note"]
    ]

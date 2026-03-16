from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union

import pandas as pd

from etf_ingest.models import ImportSummary, MetadataRecord
from etf_overlap.config import DEFAULT_DATA_DIR
from global_etf_exposure_map.app.config import ETF_HOLDINGS_DIR, METADATA_DIR

RAW_REQUIRED_COLUMNS = {
    "etf_ticker",
    "underlying_ticker",
    "company_name",
    "holding_weight",
    "sector",
}

REVENUE_COLUMNS = [
    "revenue_north_america",
    "revenue_europe",
    "revenue_asia_pacific",
    "revenue_emerging_markets",
    "revenue_latin_america",
    "revenue_middle_east_africa",
]


def load_region_metadata(metadata_csv: Optional[Path] = None) -> dict[str, MetadataRecord]:
    path = metadata_csv or (METADATA_DIR / "regions.csv")
    df = pd.read_csv(path)
    lookup: dict[str, MetadataRecord] = {}
    for _, row in df.iterrows():
        record = MetadataRecord(
            country_name=str(row["country_name"]),
            country_code=str(row["country_code"]).upper(),
            region=str(row["region"]),
            currency=str(row["currency"]).upper(),
        )
        lookup[record.country_name.lower()] = record
        lookup[record.country_code.lower()] = record
    return lookup


def infer_market_cap_bucket(market_cap: Optional[float]) -> str:
    if market_cap is None or pd.isna(market_cap):
        return "Unknown"
    if market_cap >= 200_000_000_000:
        return "Mega Cap"
    if market_cap >= 10_000_000_000:
        return "Large Cap"
    if market_cap >= 2_000_000_000:
        return "Mid Cap"
    return "Small Cap"


def default_revenue_split(region: str) -> dict[str, float]:
    key = (region or "Unknown").strip()
    values = {column: 0.0 for column in REVENUE_COLUMNS}
    mapping = {
        "North America": "revenue_north_america",
        "Europe": "revenue_europe",
        "Asia Pacific": "revenue_asia_pacific",
        "Emerging Markets": "revenue_emerging_markets",
        "Latin America": "revenue_latin_america",
        "Middle East & Africa": "revenue_middle_east_africa",
    }
    target = mapping.get(key)
    if target is None:
        values["revenue_north_america"] = 1.0
        return values
    values[target] = 1.0
    return values


def _coalesce_string(*values: Any) -> str:
    for value in values:
        if value is None:
            continue
        if isinstance(value, float) and pd.isna(value):
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _coalesce_float(*values: Any) -> Optional[float]:
    for value in values:
        if value is None:
            continue
        try:
            if pd.isna(value):
                continue
        except TypeError:
            pass
        return float(value)
    return None


def _normalize_revenue_fields(row: pd.Series, region: str) -> dict[str, float]:
    revenue_values = {column: _coalesce_float(row.get(column), 0.0) or 0.0 for column in REVENUE_COLUMNS}
    total = sum(revenue_values.values())
    if total <= 0:
        return default_revenue_split(region)
    return {column: value / total for column, value in revenue_values.items()}


def _normalize_group(df: pd.DataFrame, metadata_lookup: dict[str, MetadataRecord]) -> tuple[pd.DataFrame, str, str]:
    normalized_rows: list[dict[str, Any]] = []
    etf_ticker = str(df["etf_ticker"].iloc[0]).upper().strip()
    total_weight = float(df["holding_weight"].astype(float).sum())
    if total_weight <= 0:
        raise ValueError(f"ETF {etf_ticker} has non-positive holding weight total.")

    for _, row in df.iterrows():
        country_name = _coalesce_string(row.get("country_domicile"), row.get("country"))
        country_code = _coalesce_string(row.get("country_code")).upper()
        metadata = metadata_lookup.get(country_name.lower()) or metadata_lookup.get(country_code.lower())

        if not country_name and metadata:
            country_name = metadata.country_name
        if not country_code and metadata:
            country_code = metadata.country_code

        region = _coalesce_string(row.get("region"), metadata.region if metadata else None)
        currency = _coalesce_string(row.get("currency"), metadata.currency if metadata else None).upper()
        market_cap = _coalesce_float(row.get("market_cap"))
        market_cap_bucket = _coalesce_string(row.get("market_cap_bucket")) or infer_market_cap_bucket(market_cap)
        style_box = _coalesce_string(row.get("style_box")) or "Unknown"
        revenue_values = _normalize_revenue_fields(row, region)

        normalized_rows.append(
            {
                "etf_ticker": etf_ticker,
                "underlying_ticker": str(row["underlying_ticker"]).upper().strip(),
                "company_name": str(row["company_name"]).strip(),
                "holding_weight": float(row["holding_weight"]) / total_weight,
                "sector": str(row["sector"]).strip() or "Unknown",
                "country_domicile": country_name or "Unknown",
                "country": country_name or "Unknown",
                "country_code": country_code,
                "region": region or "Unknown",
                "currency": currency or "Unknown",
                "market_cap": market_cap,
                "market_cap_bucket": market_cap_bucket,
                "style_box": style_box,
                **revenue_values,
            }
        )

    normalized_df = pd.DataFrame(normalized_rows)
    label_region = _coalesce_string(df.get("label_region").iloc[0] if "label_region" in df.columns else None)
    if not label_region:
        label_region = (
            normalized_df.groupby("region")["holding_weight"].sum().sort_values(ascending=False).index[0]
        )
    label_focus = _coalesce_string(df.get("label_focus").iloc[0] if "label_focus" in df.columns else None)
    if not label_focus:
        label_focus = f"{label_region} Equity"
    return normalized_df, label_region, label_focus


def import_holdings_csv(
    source_csv: Union[str, Path],
    *,
    overlap_output_dir: Union[str, Path] = DEFAULT_DATA_DIR,
    global_output_dir: Union[str, Path] = ETF_HOLDINGS_DIR,
    metadata_csv: Optional[Union[str, Path]] = None,
    target: str = "both",
    overwrite: bool = False,
) -> list[ImportSummary]:
    source_path = Path(source_csv)
    df = pd.read_csv(source_path)
    missing_columns = RAW_REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"Source file is missing required columns: {sorted(missing_columns)}")

    metadata_lookup = load_region_metadata(Path(metadata_csv) if metadata_csv else None)
    overlap_dir = Path(overlap_output_dir)
    global_dir = Path(global_output_dir)
    overlap_dir.mkdir(parents=True, exist_ok=True)
    global_dir.mkdir(parents=True, exist_ok=True)

    summaries: list[ImportSummary] = []
    for etf_ticker, group in df.groupby(df["etf_ticker"].astype(str).str.upper()):
        normalized_df, label_region, label_focus = _normalize_group(group.copy(), metadata_lookup)
        overlap_path = overlap_dir / f"{etf_ticker}.csv"
        global_path = global_dir / f"{etf_ticker}.csv"

        if not overwrite:
            if target in {"both", "overlap"} and overlap_path.exists():
                raise FileExistsError(f"Overlap holdings file already exists: {overlap_path}")
            if target in {"both", "global"} and global_path.exists():
                raise FileExistsError(f"Global holdings file already exists: {global_path}")

        if target in {"both", "overlap"}:
            overlap_df = normalized_df[
                ["underlying_ticker", "company_name", "holding_weight", "sector", "country", "market_cap", "style_box"]
            ].rename(
                columns={
                    "underlying_ticker": "stock_ticker",
                    "holding_weight": "weight",
                }
            )
            overlap_df.to_csv(overlap_path, index=False)
            overlap_path_value: Optional[str] = str(overlap_path)
        else:
            overlap_path_value = None

        if target in {"both", "global"}:
            global_df = normalized_df.copy()
            global_df.insert(1, "label_region", label_region)
            global_df.insert(2, "label_focus", label_focus)
            global_columns = [
                "etf_ticker",
                "label_region",
                "label_focus",
                "underlying_ticker",
                "company_name",
                "holding_weight",
                "sector",
                "country_domicile",
                "region",
                "currency",
                "market_cap_bucket",
                "country_code",
                "revenue_north_america",
                "revenue_europe",
                "revenue_asia_pacific",
                "revenue_emerging_markets",
                "revenue_latin_america",
                "revenue_middle_east_africa",
            ]
            global_df[global_columns].to_csv(global_path, index=False)
            global_path_value: Optional[str] = str(global_path)
        else:
            global_path_value = None

        summaries.append(
            ImportSummary(
                etf_ticker=etf_ticker,
                holdings_count=len(normalized_df),
                overlap_path=overlap_path_value,
                global_path=global_path_value,
            )
        )

    return summaries

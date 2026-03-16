from __future__ import annotations

from pathlib import Path

import pandas as pd

from etf_ingest.ingestor import import_holdings_csv


def test_bulk_import_generates_overlap_and_global_files(tmp_path: Path) -> None:
    source_csv = tmp_path / "raw.csv"
    source_csv.write_text(
        "\n".join(
            [
                "etf_ticker,underlying_ticker,company_name,holding_weight,sector,country_domicile,country_code,region,currency,market_cap",
                "TEST,AAA,Alpha Inc.,60,Technology,United States,USA,North America,USD,300000000000",
                "TEST,BBB,Beta AG,40,Industrials,Germany,DEU,Europe,EUR,50000000000",
            ]
        ),
        encoding="utf-8",
    )

    overlap_dir = tmp_path / "overlap"
    global_dir = tmp_path / "global"
    summaries = import_holdings_csv(
        source_csv=source_csv,
        overlap_output_dir=overlap_dir,
        global_output_dir=global_dir,
        target="both",
        overwrite=True,
    )

    assert len(summaries) == 1
    overlap_output = overlap_dir / "TEST.csv"
    global_output = global_dir / "TEST.csv"
    assert overlap_output.exists()
    assert global_output.exists()

    overlap_df = pd.read_csv(overlap_output)
    global_df = pd.read_csv(global_output)

    assert set(overlap_df.columns) == {"stock_ticker", "company_name", "weight", "sector", "country", "market_cap", "style_box"}
    assert set(global_df.columns).issuperset({"label_region", "label_focus", "country_code", "region", "currency"})
    assert abs(float(overlap_df["weight"].sum()) - 1.0) < 1e-9
    assert abs(float(global_df["holding_weight"].sum()) - 1.0) < 1e-9


def test_bulk_import_infers_default_revenue_split(tmp_path: Path) -> None:
    source_csv = tmp_path / "raw.csv"
    source_csv.write_text(
        "\n".join(
            [
                "etf_ticker,underlying_ticker,company_name,holding_weight,sector,country_domicile,country_code,region,currency",
                "GLOB,AAA,Alpha Inc.,100,Technology,Japan,JPN,Asia Pacific,JPY",
            ]
        ),
        encoding="utf-8",
    )

    global_dir = tmp_path / "global"
    import_holdings_csv(source_csv=source_csv, global_output_dir=global_dir, target="global", overwrite=True)
    global_df = pd.read_csv(global_dir / "GLOB.csv")
    assert float(global_df.loc[0, "revenue_asia_pacific"]) == 1.0
    assert float(global_df.loc[0, "revenue_north_america"]) == 0.0

from __future__ import annotations

from pathlib import Path
from typing import Any, Union

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _to_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def plot_world_choropleth(map_ready_data: list[dict[str, Any]]) -> go.Figure:
    df = _to_frame(map_ready_data)
    return px.choropleth(
        df,
        locations="country_code",
        color="portfolio_exposure_pct",
        hover_name="country_name",
        color_continuous_scale="Blues",
        title="Portfolio Exposure by Country",
    )


def plot_region_exposure(region_exposure_table: list[dict[str, Any]]) -> go.Figure:
    df = _to_frame(region_exposure_table)
    return px.bar(df, x="name", y="exposure_pct", title="Exposure by Region", labels={"name": "Region", "exposure_pct": "Exposure (%)"})


def plot_currency_exposure(currency_exposure_table: list[dict[str, Any]]) -> go.Figure:
    df = _to_frame(currency_exposure_table)
    return px.bar(df, x="name", y="exposure_pct", title="Exposure by Currency", labels={"name": "Currency", "exposure_pct": "Exposure (%)"})


def plot_country_concentration(country_exposure_table: list[dict[str, Any]], top_n: int = 10) -> go.Figure:
    df = _to_frame(country_exposure_table).head(top_n)
    return px.bar(df, x="name", y="exposure_pct", title=f"Top {top_n} Countries by Exposure", labels={"name": "Country", "exposure_pct": "Exposure (%)"})


def plot_domicile_vs_revenue(domicile_vs_revenue_exposure: list[dict[str, Any]]) -> go.Figure:
    df = _to_frame(domicile_vs_revenue_exposure)
    melted = df.melt(
        id_vars=["name"],
        value_vars=["domicile_exposure_pct", "revenue_exposure_pct"],
        var_name="series",
        value_name="value",
    )
    return px.bar(melted, x="name", y="value", color="series", barmode="group", title="Domicile vs Revenue Exposure by Region")


def save_chart_bundle(result: dict[str, Any], output_dir: Union[str, Path]) -> list[str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    charts = {
        "world_choropleth.html": plot_world_choropleth(result["map_ready_data"]),
        "region_exposure.html": plot_region_exposure(result["region_exposure_table"]),
        "currency_exposure.html": plot_currency_exposure(result["currency_exposure_table"]),
        "country_concentration.html": plot_country_concentration(result["country_exposure_table"]),
        "domicile_vs_revenue.html": plot_domicile_vs_revenue(result["domicile_vs_revenue_exposure"]),
    }
    saved_paths: list[str] = []
    for filename, figure in charts.items():
        destination = output_path / filename
        figure.write_html(str(destination))
        saved_paths.append(str(destination))
    return saved_paths

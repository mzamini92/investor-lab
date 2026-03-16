from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_stacked_cost_breakdown(annual_breakdown: list[dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(annual_breakdown)
    return px.bar(df, x="category", y="annual_cost_dollars", color="cost_type", title="Annual Friction Breakdown")


def plot_cumulative_loss_timeline(timeline: list[dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(timeline)
    return px.line(df, x="year", y="cumulative_lost_wealth", title="Cumulative Dollars Lost Over Time")


def plot_gross_vs_net_timeline(timeline: list[dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(timeline)
    melted = df.melt(id_vars=["year"], value_vars=["gross_value", "net_value"], var_name="series", value_name="value")
    return px.line(melted, x="year", y="value", color="series", title="Gross vs Net Portfolio Growth")


def plot_comparison_chart(comparison_payload: dict[str, Any]) -> go.Figure:
    df = pd.DataFrame(
        [
            {"portfolio": "Current", "ending_value": comparison_payload["net_value_current"]},
            {"portfolio": "Alternative", "ending_value": comparison_payload["net_value_alternative"]},
        ]
    )
    return px.bar(df, x="portfolio", y="ending_value", title="Current vs Optimized Ending Value")


def save_charts(result: dict[str, Any], output_dir: str) -> list[str]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    figures = {
        "annual_cost_breakdown.html": plot_stacked_cost_breakdown(result["annual_friction_breakdown"]),
        "cumulative_loss_timeline.html": plot_cumulative_loss_timeline(result["timeline"]),
        "gross_vs_net_growth.html": plot_gross_vs_net_timeline(result["timeline"]),
    }
    saved: list[str] = []
    for name, figure in figures.items():
        path = destination / name
        figure.write_html(str(path))
        saved.append(str(path))
    return saved

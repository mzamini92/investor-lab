from __future__ import annotations

from pathlib import Path
from typing import Union

import plotly.express as px
import plotly.graph_objects as go

from globalgap.app.models import GlobalGapAnalysis


def build_exposure_pie(analysis: GlobalGapAnalysis) -> go.Figure:
    fig = px.pie(
        names=["US", "International"],
        values=[
            analysis.portfolio_exposure.portfolio_us_weight,
            analysis.portfolio_exposure.portfolio_international_weight,
        ],
        hole=0.45,
        title="Portfolio Geographic Exposure",
    )
    return fig


def build_valuation_history_chart(analysis: GlobalGapAnalysis) -> go.Figure:
    rows = analysis.visualization_data.valuation_history
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[row["date"] for row in rows], y=[row["us_forward_pe"] for row in rows], name="US PE"))
    fig.add_trace(
        go.Scatter(
            x=[row["date"] for row in rows],
            y=[row["international_forward_pe"] for row in rows],
            name="International PE",
        )
    )
    fig.update_layout(title="US vs International Valuation History", yaxis_title="Forward P/E")
    return fig


def build_dollar_cycle_chart(analysis: GlobalGapAnalysis) -> go.Figure:
    rows = analysis.visualization_data.dollar_history
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[row["date"] for row in rows], y=[row["dxy"] for row in rows], name="DXY"))
    fig.update_layout(title=f"Dollar Index ({analysis.dollar_cycle.regime.replace('_', ' ')})", yaxis_title="DXY")
    return fig


def build_analog_bar_chart(analysis: GlobalGapAnalysis) -> go.Figure:
    rows = analysis.visualization_data.analog_bars
    fig = px.bar(
        rows,
        x="date",
        y="following_5y_intl_minus_us_ann_pct",
        title="Historical Analog Outcomes: Intl Minus US Annualized",
    )
    fig.update_yaxes(title="Annualized Relative Return (%)")
    return fig


def build_simulation_chart(analysis: GlobalGapAnalysis) -> go.Figure:
    rows = analysis.visualization_data.simulation_bars
    fig = px.bar(
        rows,
        x="portfolio",
        y=["expected_annual_return_pct", "annualized_volatility_pct", "sharpe_ratio"],
        barmode="group",
        title="Current vs Diversified Portfolio Simulation",
    )
    return fig


def save_chart_bundle(analysis: GlobalGapAnalysis, output_dir: Union[str, Path]) -> dict[str, str]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    charts = {
        "exposure": build_exposure_pie(analysis),
        "valuation_history": build_valuation_history_chart(analysis),
        "dollar_cycle": build_dollar_cycle_chart(analysis),
        "historical_analogs": build_analog_bar_chart(analysis),
        "simulation": build_simulation_chart(analysis),
    }
    output_paths: dict[str, str] = {}
    for name, figure in charts.items():
        path = destination / f"{name}.html"
        figure.write_html(str(path))
        output_paths[name] = str(path)
    return output_paths

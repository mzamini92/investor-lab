from __future__ import annotations

from pathlib import Path
from typing import Any, Union

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _to_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def plot_company_exposure_bar(company_exposures: list[dict[str, Any]], top_n: int = 12) -> go.Figure:
    df = _to_frame(company_exposures).head(top_n)
    return px.bar(df, x="underlying_ticker", y="exposure_pct", color="sector", title="Top Company Exposures")


def plot_country_exposure_chart(country_exposures: list[dict[str, Any]], top_n: int = 12) -> go.Figure:
    df = _to_frame(country_exposures).head(top_n)
    return px.bar(df, x="name", y="exposure_pct", title="Country Exposure")


def plot_dependency_heatmap(heatmap_ready_data: list[dict[str, Any]]) -> go.Figure:
    df = _to_frame(heatmap_ready_data)
    return px.density_heatmap(df, x="category_group", y="display_name", z="intensity_score", color_continuous_scale="YlOrRd", title="Dependency Heatmap")


def plot_scenario_impact_chart(scenario_results: list[dict[str, Any]]) -> go.Figure:
    df = _to_frame(scenario_results)
    return px.bar(df, x="display_name", y="estimated_portfolio_impact_score", title="Scenario Impacts")


def plot_domicile_vs_revenue(domicile_vs_revenue_comparison: list[dict[str, Any]]) -> go.Figure:
    df = _to_frame(domicile_vs_revenue_comparison)
    melted = df.melt(id_vars=["name"], value_vars=["domicile_exposure_pct", "revenue_exposure_pct"], var_name="series", value_name="value")
    return px.bar(melted, x="name", y="value", color="series", barmode="group", title="Domicile vs Revenue")


def plot_world_map(map_ready_data: list[dict[str, Any]]) -> go.Figure:
    df = _to_frame(map_ready_data)
    return px.choropleth(df, locations="country_code", color="domicile_exposure_pct", hover_name="country_name", color_continuous_scale="Blues", title="Global Exposure Map")


def build_network_figure(graph_data: dict[str, Any]) -> go.Figure:
    graph = nx.DiGraph()
    for node in graph_data.get("nodes", []):
        graph.add_node(node["id"], label=node["label"], node_type=node["node_type"], weight=node["weight"])
    for edge in graph_data.get("edges", []):
        graph.add_edge(edge["source"], edge["target"], weight=edge["weight"])
    positions = nx.spring_layout(graph, seed=7)
    edge_x: list[float] = []
    edge_y: list[float] = []
    for source, target in graph.edges():
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    edge_trace = go.Scatter(x=edge_x, y=edge_y, mode="lines", line={"width": 0.6, "color": "#b8c0db"}, hoverinfo="none")
    node_trace = go.Scatter(
        x=[positions[node][0] for node in graph.nodes()],
        y=[positions[node][1] for node in graph.nodes()],
        mode="markers+text",
        text=[graph.nodes[node]["label"] for node in graph.nodes()],
        textposition="top center",
        marker={"size": [max(12.0, float(graph.nodes[node]["weight"]) * 100.0) for node in graph.nodes()], "color": "#22577a", "line": {"width": 1, "color": "#ffffff"}},
        hoverinfo="text",
    )
    return go.Figure(data=[edge_trace, node_trace]).update_layout(title="Portfolio Dependency Network", showlegend=False)


def save_chart_bundle(result: dict[str, Any], output_dir: Union[str, Path]) -> list[str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    charts = {
        "company_exposures.html": plot_company_exposure_bar(result["underlying_company_exposures"]),
        "country_exposures.html": plot_country_exposure_chart(result["country_exposures"]),
        "dependency_heatmap.html": plot_dependency_heatmap(result["heatmap_ready_data"]),
        "scenario_impacts.html": plot_scenario_impact_chart(result["scenario_results"]),
        "domicile_vs_revenue.html": plot_domicile_vs_revenue(result["domicile_vs_revenue_comparison"]),
        "world_map.html": plot_world_map(result["map_ready_data"]),
        "network_graph.html": build_network_figure(result["graph_data"]),
    }
    saved_paths: list[str] = []
    for filename, figure in charts.items():
        destination = output_path / filename
        figure.write_html(str(destination))
        saved_paths.append(str(destination))
    return saved_paths

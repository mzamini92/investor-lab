from __future__ import annotations

from pathlib import Path
from typing import Any, Union

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _to_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def plot_dependency_heatmap(heatmap_ready_data: list[dict[str, Any]]) -> go.Figure:
    df = _to_frame(heatmap_ready_data)
    return px.density_heatmap(
        df,
        x="category_group",
        y="display_name",
        z="intensity_score",
        color_continuous_scale="YlOrRd",
        title="Economic Dependency Heatmap",
    )


def plot_macro_dependency_ranking(macro_dependency_exposure_table: list[dict[str, Any]], top_n: int = 10) -> go.Figure:
    df = _to_frame(macro_dependency_exposure_table).head(top_n)
    return px.bar(
        df,
        x="display_name",
        y="exposure_pct",
        color="category_group",
        title="Top Hidden Economic Drivers",
        labels={"display_name": "Dependency", "exposure_pct": "Exposure (%)"},
    )


def plot_world_map(map_ready_data: list[dict[str, Any]]) -> go.Figure:
    df = _to_frame(map_ready_data)
    return px.choropleth(
        df,
        locations="country_code",
        color="domicile_exposure_pct",
        hover_name="country_name",
        color_continuous_scale="Blues",
        title="Global Economic Exposure Map",
    )


def plot_domicile_vs_revenue(domicile_vs_revenue_comparison: list[dict[str, Any]]) -> go.Figure:
    df = _to_frame(domicile_vs_revenue_comparison)
    melted = df.melt(
        id_vars=["name"],
        value_vars=["domicile_exposure_pct", "revenue_exposure_pct"],
        var_name="series",
        value_name="value",
    )
    return px.bar(melted, x="name", y="value", color="series", barmode="group", title="Domicile vs Revenue Exposure")


def plot_scenario_dashboard(scenario_impact_results: list[dict[str, Any]]) -> go.Figure:
    df = _to_frame(scenario_impact_results)
    return px.bar(
        df,
        x="display_name",
        y="estimated_portfolio_impact_score",
        title="Scenario Impact Dashboard",
        labels={"display_name": "Scenario", "estimated_portfolio_impact_score": "Impact Score"},
    )


def build_network_figure(network_graph_data: dict[str, Any]) -> go.Figure:
    graph = nx.DiGraph()
    for node in network_graph_data.get("nodes", []):
        graph.add_node(node["id"], label=node["label"], node_type=node["node_type"], weight=node["weight"])
    for edge in network_graph_data.get("edges", []):
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
    node_x = [positions[node][0] for node in graph.nodes()]
    node_y = [positions[node][1] for node in graph.nodes()]
    node_text = [graph.nodes[node]["label"] for node in graph.nodes()]
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="top center",
        marker={
            "size": [max(12.0, float(graph.nodes[node]["weight"]) * 100.0) for node in graph.nodes()],
            "color": "#22577a",
            "line": {"width": 1, "color": "#ffffff"},
        },
        hoverinfo="text",
    )
    return go.Figure(data=[edge_trace, node_trace]).update_layout(title="Portfolio Dependency Network", showlegend=False)


def save_chart_bundle(result: dict[str, Any], output_dir: Union[str, Path]) -> list[str]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    charts = {
        "dependency_heatmap.html": plot_dependency_heatmap(result["heatmap_ready_data"]),
        "dependency_ranking.html": plot_macro_dependency_ranking(result["macro_dependency_exposure_table"]),
        "world_map.html": plot_world_map(result["map_ready_data"]),
        "domicile_vs_revenue.html": plot_domicile_vs_revenue(result["domicile_vs_revenue_comparison"]),
        "scenario_dashboard.html": plot_scenario_dashboard(result["scenario_impact_results"]),
        "dependency_network.html": build_network_figure(result["network_graph_data"]),
    }
    saved_paths: list[str] = []
    for filename, figure in charts.items():
        destination = output_path / filename
        figure.write_html(str(destination))
        saved_paths.append(str(destination))
    return saved_paths

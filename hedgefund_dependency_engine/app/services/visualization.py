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


def build_network_figure(
    graph_data: dict[str, Any],
    *,
    included_node_types: list[str] | None = None,
    min_edge_weight: float = 0.0,
    show_labels: bool = True,
    layout_algorithm: str = "spring",
) -> go.Figure:
    graph = nx.DiGraph()
    allowed_node_types = set(included_node_types or [])
    for node in graph_data.get("nodes", []):
        node_type = str(node["node_type"])
        if allowed_node_types and node_type not in allowed_node_types:
            continue
        graph.add_node(node["id"], label=node["label"], node_type=node_type, weight=node["weight"])
    for edge in graph_data.get("edges", []):
        weight = float(edge["weight"])
        if weight < float(min_edge_weight):
            continue
        if edge["source"] in graph and edge["target"] in graph:
            graph.add_edge(edge["source"], edge["target"], weight=weight)

    if not graph.nodes:
        return go.Figure().update_layout(
            title="Portfolio Dependency Network",
            annotations=[
                {
                    "text": "No graph nodes remain after applying the current filters.",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16},
                }
            ],
        )

    if layout_algorithm == "kamada_kawai":
        positions = nx.kamada_kawai_layout(graph)
    elif layout_algorithm == "circular":
        positions = nx.circular_layout(graph)
    else:
        positions = nx.spring_layout(graph, seed=7)

    edge_x: list[float] = []
    edge_y: list[float] = []
    edge_text: list[str] = []
    for source, target, data in graph.edges(data=True):
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_text.extend([f"{graph.nodes[source]['label']} -> {graph.nodes[target]['label']}<br>Strength: {float(data['weight']):.4f}"] * 2 + [None])
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line={"width": 0.8, "color": "#b8c0db"},
        text=edge_text,
        hovertemplate="%{text}<extra></extra>",
    )
    color_map = {
        "portfolio": "#0f172a",
        "etf": "#2563eb",
        "company": "#10b981",
        "dependency": "#f59e0b",
        "country": "#7c3aed",
        "region": "#db2777",
        "currency": "#ea580c",
    }
    node_labels = [graph.nodes[node]["label"] for node in graph.nodes()]
    node_types = [graph.nodes[node]["node_type"] for node in graph.nodes()]
    node_trace = go.Scatter(
        x=[positions[node][0] for node in graph.nodes()],
        y=[positions[node][1] for node in graph.nodes()],
        mode="markers+text" if show_labels else "markers",
        text=node_labels if show_labels else None,
        textposition="top center",
        customdata=[[node_type, float(graph.nodes[node]["weight"])] for node, node_type in zip(graph.nodes(), node_types)],
        marker={
            "size": [max(14.0, float(graph.nodes[node]["weight"]) * 120.0) for node in graph.nodes()],
            "color": [color_map.get(node_type, "#22577a") for node_type in node_types],
            "line": {"width": 1, "color": "#ffffff"},
        },
        hovertemplate="<b>%{text}</b><br>Type: %{customdata[0]}<br>Weight: %{customdata[1]:.4f}<extra></extra>",
    )
    return go.Figure(data=[edge_trace, node_trace]).update_layout(
        title="Portfolio Dependency Network",
        showlegend=False,
        dragmode="pan",
        hovermode="closest",
        margin={"l": 10, "r": 10, "t": 50, "b": 10},
        xaxis={"showgrid": False, "zeroline": False, "visible": False},
        yaxis={"showgrid": False, "zeroline": False, "visible": False},
        plot_bgcolor="rgba(248,250,252,1)",
        paper_bgcolor="rgba(248,250,252,1)",
    )


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

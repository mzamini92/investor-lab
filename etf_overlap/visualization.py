from __future__ import annotations

from typing import Any
from typing import Union

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from etf_overlap.models import AnalysisResult


def _as_result_dict(result: Union[AnalysisResult, dict[str, Any]]) -> dict[str, Any]:
    return result.to_dict() if isinstance(result, AnalysisResult) else result


def plot_top_holdings_bar(result: Union[AnalysisResult, dict[str, Any]], top_n: int = 10) -> go.Figure:
    payload = _as_result_dict(result)
    df = pd.DataFrame(payload["underlying_exposures"]).head(top_n)
    return px.bar(
        df,
        x="stock_ticker",
        y="exposure_pct",
        color="sector",
        title=f"Top {top_n} Underlying Holdings Exposure",
        labels={"stock_ticker": "Ticker", "exposure_pct": "Exposure (%)"},
    )


def plot_sector_exposure_chart(result: Union[AnalysisResult, dict[str, Any]]) -> go.Figure:
    payload = _as_result_dict(result)
    df = pd.DataFrame(payload["sector_exposures"])
    return px.pie(df, values="exposure_pct", names="name", title="Sector Exposure")


def plot_overlap_heatmap(result: Union[AnalysisResult, dict[str, Any]]) -> go.Figure:
    payload = _as_result_dict(result)
    tickers = sorted(payload["overlap_matrix"])
    z_values = []
    for row_ticker in tickers:
        row = []
        for col_ticker in tickers:
            row.append(payload["overlap_matrix"][row_ticker][col_ticker]["weighted_overlap"] * 100.0)
        z_values.append(row)

    return go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=tickers,
            y=tickers,
            colorscale="Blues",
            text=[[f"{value:.1f}%" for value in row] for row in z_values],
            texttemplate="%{text}",
        )
    ).update_layout(title="ETF Weighted Overlap Heatmap", xaxis_title="ETF", yaxis_title="ETF")


def plot_overlap_network_graph(
    result: Union[AnalysisResult, dict[str, Any]],
    threshold: float = 0.20,
) -> plt.Figure:
    payload = _as_result_dict(result)
    graph = nx.Graph()

    for position in payload["normalized_portfolio"]:
        graph.add_node(position["ticker"], size=position["portfolio_weight"] * 4000.0)

    for pair in payload["overlap_pairs"]:
        if float(pair["weighted_overlap"]) >= threshold:
            graph.add_edge(
                pair["etf_a"],
                pair["etf_b"],
                weight=float(pair["weighted_overlap"]),
                label=f"{float(pair['weighted_overlap']):.0%}",
            )

    figure, axis = plt.subplots(figsize=(8, 6))
    if graph.number_of_edges() == 0:
        axis.text(0.5, 0.5, "No overlap edges above threshold", ha="center", va="center")
        axis.axis("off")
        return figure

    positions = nx.spring_layout(graph, seed=7)
    node_sizes = [graph.nodes[node]["size"] for node in graph.nodes]
    edge_widths = [graph.edges[edge]["weight"] * 10.0 for edge in graph.edges]
    nx.draw_networkx_nodes(graph, positions, node_size=node_sizes, node_color="#22577a", ax=axis)
    nx.draw_networkx_labels(graph, positions, font_color="white", ax=axis)
    nx.draw_networkx_edges(graph, positions, width=edge_widths, edge_color="#95d5b2", ax=axis)
    edge_labels = {(u, v): graph.edges[(u, v)]["label"] for u, v in graph.edges}
    nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels, font_size=9, ax=axis)
    axis.set_title("ETF Overlap Network")
    axis.axis("off")
    return figure

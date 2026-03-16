from __future__ import annotations

from typing import Any

import networkx as nx
import pandas as pd

from hedgefund_dependency_engine.app.config import DEPENDENCY_COLUMNS


def build_multilayer_graph(frame: pd.DataFrame) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node("portfolio", label="Portfolio", node_type="portfolio", weight=1.0)
    for etf_ticker, etf_frame in frame.groupby("etf_ticker"):
        etf_id = f"etf::{etf_ticker}"
        etf_weight = float(etf_frame["fund_weight"].iloc[0])
        graph.add_node(etf_id, label=etf_ticker, node_type="etf", weight=etf_weight)
        graph.add_edge("portfolio", etf_id, weight=etf_weight)
        for _, row in etf_frame.iterrows():
            company_id = f"company::{row['underlying_ticker']}"
            company_weight = float(row["company_exposure"])
            if company_id not in graph:
                graph.add_node(company_id, label=str(row["underlying_ticker"]), node_type="company", weight=company_weight)
            graph.add_edge(etf_id, company_id, weight=company_weight)

            country_id = f"country::{row['country_domicile']}"
            region_id = f"region::{row['region']}"
            currency_id = f"currency::{row['currency']}"
            for node_id, label, node_type in (
                (country_id, str(row["country_domicile"]), "country"),
                (region_id, str(row["region"]), "region"),
                (currency_id, str(row["currency"]), "currency"),
            ):
                if node_id not in graph:
                    graph.add_node(node_id, label=label, node_type=node_type, weight=0.0)
                graph.add_edge(company_id, node_id, weight=company_weight)

            for dependency_name, metadata in DEPENDENCY_COLUMNS.items():
                score = float(row[dependency_name])
                if score <= 0:
                    continue
                dependency_id = f"dependency::{dependency_name}"
                if dependency_id not in graph:
                    graph.add_node(dependency_id, label=metadata["display_name"], node_type="dependency", weight=score)
                graph.add_edge(company_id, dependency_id, weight=company_weight * score)
    return graph


def graph_to_payload(graph: nx.DiGraph) -> dict[str, Any]:
    return {
        "nodes": [
            {"id": node, "label": data.get("label", node), "node_type": data.get("node_type", "unknown"), "weight": float(data.get("weight", 0.0))}
            for node, data in graph.nodes(data=True)
        ],
        "edges": [
            {"source": source, "target": target, "weight": float(data.get("weight", 0.0))}
            for source, target, data in graph.edges(data=True)
        ],
    }


def compute_graph_centrality(graph: nx.DiGraph) -> dict[str, list[dict[str, Any]]]:
    undirected = graph.to_undirected()
    degree_centrality = nx.degree_centrality(undirected)
    betweenness = nx.betweenness_centrality(undirected, weight="weight", normalized=True)
    try:
        eigenvector = nx.eigenvector_centrality_numpy(undirected, weight="weight")
    except Exception:
        eigenvector = {node: 0.0 for node in graph.nodes()}

    rows = []
    for node, data in graph.nodes(data=True):
        rows.append(
            {
                "node_id": node,
                "label": data.get("label", node),
                "node_type": data.get("node_type", "unknown"),
                "weighted_degree": float(undirected.degree(node, weight="weight")),
                "degree_centrality": float(degree_centrality.get(node, 0.0)),
                "betweenness_centrality": float(betweenness.get(node, 0.0)),
                "eigenvector_centrality": float(eigenvector.get(node, 0.0)),
            }
        )
    centrality_df = pd.DataFrame(rows)
    result: dict[str, list[dict[str, Any]]] = {}
    for node_type in sorted(centrality_df["node_type"].unique()):
        subset = centrality_df.loc[centrality_df["node_type"] == node_type].sort_values(
            ["weighted_degree", "betweenness_centrality"], ascending=[False, False]
        )
        result[node_type] = subset.head(10).to_dict(orient="records")
    result["all_nodes"] = centrality_df.sort_values(["weighted_degree", "betweenness_centrality"], ascending=[False, False]).head(25).to_dict(orient="records")
    return result

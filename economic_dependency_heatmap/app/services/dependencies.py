from __future__ import annotations

from typing import Any

import pandas as pd

from economic_dependency_heatmap.app.config import DEPENDENCY_COLUMNS


def aggregate_macro_dependency_exposure(constituent_frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for dependency_name, metadata in DEPENDENCY_COLUMNS.items():
        exposure = float((constituent_frame["exposure"] * constituent_frame[dependency_name]).sum())
        rows.append(
            {
                "dependency_name": dependency_name,
                "display_name": metadata["display_name"],
                "category_group": metadata["category_group"],
                "exposure": exposure,
                "exposure_pct": exposure * 100.0,
            }
        )
    return pd.DataFrame(rows).sort_values(["exposure", "display_name"], ascending=[False, True]).reset_index(drop=True)


def build_heatmap_ready_data(dependency_exposure_df: pd.DataFrame) -> pd.DataFrame:
    max_exposure = float(dependency_exposure_df["exposure"].max()) if not dependency_exposure_df.empty else 0.0
    df = dependency_exposure_df.copy()
    df["intensity_score"] = 0.0 if max_exposure <= 0 else (df["exposure"] / max_exposure) * 100.0
    return df[["dependency_name", "display_name", "exposure_pct", "category_group", "intensity_score"]]


def build_dependency_network(constituent_frame: pd.DataFrame) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = [{"id": "portfolio", "label": "Portfolio", "node_type": "portfolio", "weight": 1.0}]
    edges: list[dict[str, Any]] = []
    etf_nodes: set[str] = set()
    company_nodes: set[str] = set()
    dependency_nodes: set[str] = set()

    for etf_ticker, etf_frame in constituent_frame.groupby("etf_ticker"):
        etf_weight = float(etf_frame["fund_weight"].iloc[0])
        etf_id = f"etf::{etf_ticker}"
        if etf_id not in etf_nodes:
            nodes.append({"id": etf_id, "label": etf_ticker, "node_type": "etf", "weight": etf_weight})
            etf_nodes.add(etf_id)
            edges.append({"source": "portfolio", "target": etf_id, "weight": etf_weight})

        for _, row in etf_frame.iterrows():
            company_id = f"company::{row['underlying_ticker']}"
            if company_id not in company_nodes:
                nodes.append(
                    {
                        "id": company_id,
                        "label": str(row["underlying_ticker"]),
                        "node_type": "company",
                        "weight": float(row["exposure"]),
                    }
                )
                company_nodes.add(company_id)
            edges.append({"source": etf_id, "target": company_id, "weight": float(row["exposure"])})

            dependency_profile = {name: float(row[name]) for name in DEPENDENCY_COLUMNS}
            ranked_dependencies = sorted(dependency_profile.items(), key=lambda item: item[1], reverse=True)[:4]
            for dependency_name, score in ranked_dependencies:
                if score <= 0:
                    continue
                dependency_id = f"dependency::{dependency_name}"
                if dependency_id not in dependency_nodes:
                    nodes.append(
                        {
                            "id": dependency_id,
                            "label": DEPENDENCY_COLUMNS[dependency_name]["display_name"],
                            "node_type": "dependency",
                            "weight": score,
                        }
                    )
                    dependency_nodes.add(dependency_id)
                edges.append({"source": company_id, "target": dependency_id, "weight": float(row["exposure"]) * score})
    return {"nodes": nodes, "edges": edges}

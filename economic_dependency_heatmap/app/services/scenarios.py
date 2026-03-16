from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from economic_dependency_heatmap.app.config import DEPENDENCY_COLUMNS
from economic_dependency_heatmap.app.models import MacroScenario


def compute_scenario_impacts(
    constituent_frame: pd.DataFrame,
    scenarios: list[MacroScenario],
    selected_names: Optional[list[str]] = None,
) -> list[dict[str, Any]]:
    if selected_names:
        allowed_names = {name.strip() for name in selected_names}
        scenarios = [scenario for scenario in scenarios if scenario.name in allowed_names]

    results: list[dict[str, Any]] = []
    for scenario in scenarios:
        dependency_contributions = []
        for dependency_name, shock_weight in scenario.shock_weights.items():
            if dependency_name not in constituent_frame.columns:
                continue
            exposure = float((constituent_frame["exposure"] * constituent_frame[dependency_name]).sum())
            contribution = exposure * float(shock_weight)
            dependency_contributions.append(
                {
                    "dependency_name": dependency_name,
                    "display_name": DEPENDENCY_COLUMNS[dependency_name]["display_name"],
                    "shock_weight": float(shock_weight),
                    "exposure": exposure,
                    "contribution": contribution,
                }
            )

        company_rows: list[dict[str, Any]] = []
        for underlying_ticker, company_frame in constituent_frame.groupby("underlying_ticker"):
            sensitivity = 0.0
            company_exposure = float(company_frame["exposure"].sum())
            for dependency_name, shock_weight in scenario.shock_weights.items():
                sensitivity += float(company_frame[dependency_name].iloc[0]) * float(shock_weight)
            contribution = company_exposure * sensitivity
            company_rows.append(
                {
                    "underlying_ticker": underlying_ticker,
                    "company_name": str(company_frame["company_name"].iloc[0]),
                    "exposure": company_exposure,
                    "scenario_sensitivity": sensitivity,
                    "contribution": contribution,
                }
            )

        dependency_contributions = sorted(
            dependency_contributions,
            key=lambda row: abs(float(row["contribution"])),
            reverse=True,
        )
        company_rows = sorted(company_rows, key=lambda row: abs(float(row["contribution"])), reverse=True)
        estimated_impact = sum(float(row["contribution"]) for row in dependency_contributions)
        results.append(
            {
                "scenario_name": scenario.name,
                "display_name": scenario.display_name,
                "description": scenario.description,
                "estimated_portfolio_impact_score": round(estimated_impact, 6),
                "top_contributing_dependencies": dependency_contributions[:5],
                "top_contributing_companies": company_rows[:5],
            }
        )
    return results

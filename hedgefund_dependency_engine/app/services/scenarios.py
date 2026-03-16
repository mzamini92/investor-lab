from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from hedgefund_dependency_engine.app.config import DEPENDENCY_COLUMNS
from hedgefund_dependency_engine.app.models import EventTemplate, MacroScenario


def build_dynamic_scenarios(
    event_templates: list[EventTemplate],
    dynamic_events: Optional[list[dict[str, Any]]] = None,
    headline_context: Optional[str] = None,
) -> list[MacroScenario]:
    template_map = {template.name: template for template in event_templates}
    selected: dict[str, tuple[EventTemplate, float, str | None]] = {}

    for event in dynamic_events or []:
        name = str(event.get("name", "")).strip()
        if not name or name not in template_map:
            continue
        severity = float(event.get("severity", template_map[name].default_severity))
        selected[name] = (template_map[name], severity, None)

    headline_text = (headline_context or "").strip().lower()
    if headline_text:
        for template in event_templates:
            if any(keyword in headline_text for keyword in template.trigger_keywords):
                severity = selected.get(template.name, (template, template.default_severity, None))[1]
                selected[template.name] = (template, severity, "headline match")

    return [
        template.to_macro_scenario(severity=severity, source_note=source_note)
        for template, severity, source_note in selected.values()
    ]


def event_templates_to_rows(event_templates: list[EventTemplate]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for template in event_templates:
        rows.append(
            {
                "name": template.name,
                "display_name": template.display_name,
                "description": template.description,
                "default_severity": template.default_severity,
                "trigger_keywords": template.trigger_keywords,
            }
        )
    return rows


def compute_scenario_impacts(frame: pd.DataFrame, scenarios: list[MacroScenario], selected_names: Optional[list[str]] = None) -> list[dict[str, Any]]:
    if selected_names:
        allowed = {name.strip() for name in selected_names}
        scenarios = [scenario for scenario in scenarios if scenario.name in allowed]

    results: list[dict[str, Any]] = []
    for scenario in scenarios:
        dependency_contributions = []
        for dependency_name, shock_weight in scenario.shock_weights.items():
            exposure = float((frame["company_exposure"] * frame[dependency_name]).sum())
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
        for company_ticker, company_frame in frame.groupby("underlying_ticker"):
            company_exposure = float(company_frame["company_exposure"].sum())
            company_sensitivity = sum(float(company_frame[dependency_name].iloc[0]) * float(weight) for dependency_name, weight in scenario.shock_weights.items())
            company_rows.append(
                {
                    "underlying_ticker": company_ticker,
                    "company_name": str(company_frame["company_name"].iloc[0]),
                    "exposure": company_exposure,
                    "scenario_sensitivity": company_sensitivity,
                    "contribution": company_exposure * company_sensitivity,
                }
            )

        etf_rows: list[dict[str, Any]] = []
        for etf_ticker, etf_frame in frame.groupby("etf_ticker"):
            contribution = 0.0
            for _, row in etf_frame.iterrows():
                row_sensitivity = sum(float(row[dependency_name]) * float(weight) for dependency_name, weight in scenario.shock_weights.items())
                contribution += float(row["company_exposure"]) * row_sensitivity
            etf_rows.append(
                {
                    "etf_ticker": etf_ticker,
                    "fund_weight": float(etf_frame["fund_weight"].iloc[0]),
                    "contribution": contribution,
                }
            )

        dependency_contributions = sorted(dependency_contributions, key=lambda item: abs(float(item["contribution"])), reverse=True)
        company_rows = sorted(company_rows, key=lambda item: abs(float(item["contribution"])), reverse=True)
        etf_rows = sorted(etf_rows, key=lambda item: abs(float(item["contribution"])), reverse=True)
        total_impact = sum(float(item["contribution"]) for item in dependency_contributions)
        explanation = (
            f"{scenario.display_name} primarily transmits through "
            f"{dependency_contributions[0]['display_name'] if dependency_contributions else 'macro dependencies'} "
            f"and the leading ETF contributor is {etf_rows[0]['etf_ticker'] if etf_rows else 'N/A'}."
        )
        results.append(
            {
                "scenario_name": scenario.name,
                "display_name": scenario.display_name,
                "description": scenario.description,
                "estimated_portfolio_impact_score": total_impact,
                "top_contributing_dependencies": dependency_contributions[:5],
                "top_contributing_companies": company_rows[:5],
                "top_contributing_etfs": etf_rows[:5],
                "explanation": explanation,
            }
        )
    return results

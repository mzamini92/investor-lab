from __future__ import annotations

from typing import Any


def generate_warnings(
    *,
    normalized_portfolio: list[dict[str, Any]],
    dependency_exposures: list[dict[str, Any]],
    country_exposures: list[dict[str, Any]],
    overlap_pairs: list[dict[str, Any]],
    diversification_scores: dict[str, float],
    graph_centrality: dict[str, list[dict[str, Any]]],
) -> list[str]:
    warnings: list[str] = []
    if dependency_exposures and float(dependency_exposures[0]["exposure"]) >= 0.35:
        warnings.append(
            f"Your portfolio appears diversified across {len(normalized_portfolio)} ETFs, but {float(dependency_exposures[0]['exposure']):.1%} of dependency exposure is tied to {dependency_exposures[0]['display_name']}."
        )
    if country_exposures and float(country_exposures[0]["exposure"]) >= 0.50:
        warnings.append(
            f"Country concentration is elevated: {country_exposures[0]['name']} represents {float(country_exposures[0]['exposure']):.1%} of look-through exposure."
        )
    for pair in overlap_pairs:
        if float(pair["weighted_overlap"]) >= 0.70 and float(pair["practical_overlap_contribution"]) >= 0.08:
            warnings.append(
                f"{pair['etf_a']} and {pair['etf_b']} are materially redundant with {float(pair['weighted_overlap']):.1%} weighted overlap."
            )
            break
    centrality_nodes = graph_centrality.get("company", [])
    if centrality_nodes:
        warnings.append(
            f"The dependency graph is centered on {centrality_nodes[0]['label']}, a major concentration hub."
        )
    if float(diversification_scores["economic_reality_gap"]) >= 45:
        warnings.append(
            f"Economic Reality Gap is high at {float(diversification_scores['economic_reality_gap']):.1f}/100."
        )
    return warnings


def generate_summary_insights(
    *,
    dependency_exposures: list[dict[str, Any]],
    revenue_exposures: list[dict[str, Any]],
    graph_centrality: dict[str, list[dict[str, Any]]],
    diversification_scores: dict[str, float],
) -> list[str]:
    insights = [
        f"Global Diversification Score: {float(diversification_scores['global_diversification_score']):.1f}/100.",
        f"Economic Reality Gap: {float(diversification_scores['economic_reality_gap']):.1f}/100.",
        f"Macro Dependence Score: {float(diversification_scores['macro_dependence_score']):.1f}/100.",
    ]
    if dependency_exposures:
        insights.append(
            f"Top hidden macro driver is {dependency_exposures[0]['display_name']} at {float(dependency_exposures[0]['exposure']):.1%}."
        )
    if revenue_exposures:
        insights.append(
            f"Top revenue demand center is {revenue_exposures[0]['name']} at {float(revenue_exposures[0]['exposure']):.1%}."
        )
    company_hubs = graph_centrality.get("company", [])
    if company_hubs:
        top_hubs = ", ".join(node["label"] for node in company_hubs[:3])
        insights.append(f"Top graph centrality hubs are {top_hubs}.")
    return insights

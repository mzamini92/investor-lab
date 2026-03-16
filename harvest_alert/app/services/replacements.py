from __future__ import annotations

from typing import Any

from harvest_alert.app.models import ReplacementSecurity
from harvest_alert.app.services.similarity import compute_similarity


def build_universe_map(replacements: list[ReplacementSecurity]) -> dict[str, ReplacementSecurity]:
    return {item.ticker: item for item in replacements}


def recommend_replacements(
    ticker: str,
    universe: list[ReplacementSecurity],
) -> list[dict[str, Any]]:
    universe_map = build_universe_map(universe)
    original = universe_map.get(ticker.upper())
    if original is None:
        return []

    rows: list[dict[str, Any]] = []
    for candidate in universe:
        if candidate.ticker == original.ticker:
            continue
        if original.ticker in candidate.prohibited_as_replacement_for:
            continue
        if candidate.ticker in original.prohibited_as_replacement_for:
            continue
        if original.ticker in candidate.similar_to or candidate.asset_class == original.asset_class:
            similarity_score, drift_summary, drift_warnings = compute_similarity(original, candidate)
            if similarity_score < 55:
                continue
            rows.append(
                {
                    "ticker": candidate.ticker,
                    "security_name": candidate.security_name,
                    "similarity_score": similarity_score,
                    "strategy_preservation_summary": drift_summary,
                    "drift_warnings": drift_warnings,
                    "expense_ratio_difference": round(candidate.expense_ratio - original.expense_ratio, 6),
                    "benchmark_index": candidate.benchmark_index,
                }
            )
    return sorted(rows, key=lambda item: (-item["similarity_score"], item["expense_ratio_difference"]))

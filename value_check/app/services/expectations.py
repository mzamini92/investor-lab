from __future__ import annotations

from typing import Any


def build_implied_expectations(
    current_metrics: dict[str, Any],
    historical_rows: list[dict[str, Any]],
) -> dict[str, str]:
    pe_row = next((row for row in historical_rows if row["metric"] == "pe_ratio" and row["percentile_rank"] is not None), None)
    ps_row = next((row for row in historical_rows if row["metric"] == "ps_ratio" and row["percentile_rank"] is not None), None)
    spread = current_metrics.get("treasury_relative_fcf_spread")

    stretch_level = "moderate"
    summary = "The current valuation does not look disconnected from normal expectations."

    if pe_row and pe_row["percentile_rank"] >= 85:
        stretch_level = "very_high"
        summary = "At this valuation, the market appears to be pricing in several years of above-normal execution."
    elif ps_row and ps_row["percentile_rank"] >= 80:
        stretch_level = "high"
        summary = "The current sales multiple suggests investors are already paying up for durable growth."
    elif spread is not None and spread <= -0.02:
        stretch_level = "high"
        summary = "The cash-flow yield is meaningfully below the Treasury yield, which suggests investors are accepting a rich valuation for future growth."
    elif pe_row and pe_row["percentile_rank"] <= 30:
        stretch_level = "low"
        summary = "The current multiple does not appear to require heroic assumptions relative to the company’s own history."

    return {
        "summary": summary,
        "stretch_level": stretch_level,
    }

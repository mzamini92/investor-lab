from __future__ import annotations

from typing import Any, Optional

import pandas as pd


def consecutive_negative_streak(history_df: pd.DataFrame, column: str, threshold: float = 0.0) -> int:
    streak = 0
    values = pd.to_numeric(history_df[column], errors="coerce").dropna().tolist()
    for value in reversed(values):
        if value < threshold:
            streak += 1
        else:
            break
    return streak


def build_transition_label(
    current_score: float,
    prior_score: Optional[float],
    current_label: str,
    prior_label: Optional[str],
) -> str:
    if prior_score is None or prior_label is None:
        return "new coverage"
    if current_label == prior_label and abs(current_score - prior_score) < 3:
        return "stable"
    if current_score - prior_score >= 6:
        return "strengthening"
    if current_score - prior_score <= -10:
        return "clear deterioration"
    if current_score - prior_score < 0:
        return "early erosion"
    return "recovery"


def build_history_table(score_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(score_rows, key=lambda row: row["quarter"])

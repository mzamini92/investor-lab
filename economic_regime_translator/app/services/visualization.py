from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def build_score_bar_chart(scorecard: dict[str, float]) -> go.Figure:
    df = pd.DataFrame([{"score": key, "value": value} for key, value in scorecard.items()])
    return px.bar(df, x="score", y="value", title="Regime Scorecard")


def build_analog_similarity_chart(analogs: list[dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(analogs)
    if df.empty:
        return go.Figure()
    return px.bar(df, x="observation_date", y="similarity_score", color="regime_label", title="Historical Analogs")


def build_transition_chart(current: dict[str, float], prior: dict[str, float]) -> go.Figure:
    df = pd.DataFrame(
        [{"score": key, "value": value, "snapshot": "Current"} for key, value in current.items()]
        + [{"score": key, "value": value, "snapshot": "Prior"} for key, value in prior.items()]
    )
    return px.bar(df, x="score", y="value", color="snapshot", barmode="group", title="Scorecard Change")

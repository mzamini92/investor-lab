from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_moat_score_history(history_rows: list[dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(history_rows)
    if df.empty:
        return go.Figure()
    return px.line(df, x="quarter", y="moat_health_score", markers=True, title="Moat Score History")


def plot_signal_radar(signal_rows: list[dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(signal_rows)
    if df.empty:
        return go.Figure()
    return go.Figure(
        data=[
            go.Scatterpolar(
                r=df["strength_score"],
                theta=df["signal_name"],
                fill="toself",
                name="Signal strength",
            )
        ],
        layout=go.Layout(title="Moat Signal Scorecard", polar={"radialaxis": {"visible": True, "range": [0, 100]}}),
    )


def plot_peer_comparison(peer_rows: list[dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(peer_rows)
    if df.empty:
        return go.Figure()
    return px.bar(df, x="metric", y="premium_discount_vs_peer_median", color="peer_interpretation", title="Peer Relative Moat Comparison")

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_percentile_bars(historical_rows: list[dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(historical_rows)
    if df.empty:
        return go.Figure()
    return px.bar(df, x="metric", y="percentile_rank", color="metric_interpretation", title="Valuation vs Own History")


def plot_peer_comparison(peer_rows: list[dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(peer_rows)
    if df.empty:
        return go.Figure()
    return px.bar(df, x="metric", y="premium_discount_vs_peer_median", color="peer_interpretation", title="Premium / Discount vs Peers")


def plot_scorecard(result: dict[str, Any]) -> go.Figure:
    rows = [
        {"name": "Composite Score", "value": result["composite_score"]},
        {"name": "Confidence Score", "value": result["confidence_score"]},
    ]
    return px.bar(pd.DataFrame(rows), x="name", y="value", title="ValueCheck Scorecard")

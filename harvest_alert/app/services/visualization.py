from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_losses(opportunities: list[dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(opportunities)
    if df.empty:
        return go.Figure()
    return px.bar(df, x="ticker", y="harvestable_loss", color="wash_sale_risk_level", title="Harvestable Losses")


def plot_tax_savings(opportunities: list[dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(opportunities)
    if df.empty:
        return go.Figure()
    return px.bar(df, x="ticker", y="estimated_tax_savings", color="wash_sale_risk_level", title="Estimated Tax Savings")


def plot_similarity(opportunities: list[dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(opportunities)
    if df.empty:
        return go.Figure()
    return px.bar(df, x="ticker", y="replacement_similarity_score", color="wash_sale_risk_level", title="Replacement Similarity")

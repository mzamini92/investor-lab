from __future__ import annotations

import pandas as pd

from globalgap.app.config import DOLLAR_HISTORY_FILE
from globalgap.app.models import DollarCycle


def load_dollar_history() -> pd.DataFrame:
    df = pd.read_csv(DOLLAR_HISTORY_FILE, parse_dates=["date"])
    return df.sort_values("date").reset_index(drop=True)


def analyze_dollar_cycle() -> tuple[DollarCycle, pd.DataFrame]:
    history = load_dollar_history()
    current = history.iloc[-1]
    window = history.tail(min(len(history), 20))
    percentile = float((window["dxy"] <= current["dxy"]).mean()) * 100
    lookback_row = history.iloc[max(0, len(history) - 5)]
    trend_delta = float(current["dxy"] - lookback_row["dxy"])

    if trend_delta <= -2.0:
        trend = "falling"
    elif trend_delta >= 2.0:
        trend = "rising"
    else:
        trend = "flat"

    if percentile >= 80 and trend == "falling":
        regime = "PEAK_DOLLAR"
    elif percentile >= 70 and trend == "rising":
        regime = "STRONG_DOLLAR"
    elif percentile <= 30 and trend == "falling":
        regime = "WEAK_DOLLAR"
    else:
        regime = "WEAKENING_DOLLAR" if trend == "falling" else "STRONG_DOLLAR"

    narrative_map = {
        "PEAK_DOLLAR": "The dollar is still historically elevated, but momentum has rolled over. That has often helped international equities regain relative performance leadership.",
        "STRONG_DOLLAR": "A firm dollar has supported US relative performance historically, but it can also create a headwind for foreign equity returns when translated back to USD.",
        "WEAKENING_DOLLAR": "A weakening dollar has historically improved the setup for international diversification by easing the translation headwind for non-US returns.",
        "WEAK_DOLLAR": "A weak dollar regime has often coincided with stronger relative performance from international and commodity-sensitive markets.",
    }

    result = DollarCycle(
        as_of=current["date"].date().isoformat(),
        dxy=round(float(current["dxy"]), 2),
        reer=round(float(current["reer"]), 2),
        dxy_percentile_10y=round(percentile, 2),
        dxy_trend=trend,
        regime=regime,
        narrative=narrative_map[regime],
    )
    return result, history

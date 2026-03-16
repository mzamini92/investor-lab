from __future__ import annotations

import pandas as pd

from globalgap.app.config import VALUATION_HISTORY_FILE
from globalgap.app.models import ValuationGap


def load_valuation_history() -> pd.DataFrame:
    df = pd.read_csv(VALUATION_HISTORY_FILE, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["valuation_spread_ratio"] = df["us_forward_pe"] / df["international_forward_pe"]
    return df


def analyze_valuation_gap() -> tuple[ValuationGap, pd.DataFrame]:
    history = load_valuation_history()
    current = history.iloc[-1]
    percentile = float(history["valuation_spread_ratio"].rank(pct=True).iloc[-1]) * 100
    premium = (current["valuation_spread_ratio"] - 1.0) * 100
    intl_discount = (1.0 - (current["international_forward_pe"] / current["us_forward_pe"])) * 100
    narrative = (
        f"International equities trade at a {intl_discount:.1f}% valuation discount to US equities "
        f"based on current forward earnings multiples."
    )
    gap = ValuationGap(
        as_of=current["date"].date().isoformat(),
        us_forward_pe=round(float(current["us_forward_pe"]), 2),
        international_forward_pe=round(float(current["international_forward_pe"]), 2),
        valuation_spread_ratio=round(float(current["valuation_spread_ratio"]), 4),
        us_premium_pct=round(float(premium), 2),
        international_discount_pct=round(float(intl_discount), 2),
        spread_percentile_vs_history=round(percentile, 2),
        narrative=narrative,
    )
    return gap, history

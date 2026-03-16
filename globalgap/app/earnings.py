from __future__ import annotations

import pandas as pd

from globalgap.app.config import EARNINGS_GROWTH_FILE
from globalgap.app.models import EarningsGrowthGap


def load_earnings_growth_history() -> pd.DataFrame:
    df = pd.read_csv(EARNINGS_GROWTH_FILE, parse_dates=["date"])
    return df.sort_values("date").reset_index(drop=True)


def analyze_earnings_growth_gap() -> tuple[EarningsGrowthGap, pd.DataFrame]:
    history = load_earnings_growth_history()
    current = history.iloc[-1]
    gap = float(current["international_earnings_growth_pct"] - current["us_earnings_growth_pct"])
    if gap > 0:
        narrative = (
            f"International earnings growth is projected to exceed US earnings growth by {gap:.1f} percentage points."
        )
    elif gap < 0:
        narrative = f"US earnings growth is projected to exceed international earnings growth by {abs(gap):.1f} percentage points."
    else:
        narrative = "US and international earnings growth expectations are currently roughly in line."

    result = EarningsGrowthGap(
        as_of=current["date"].date().isoformat(),
        us_earnings_growth_pct=round(float(current["us_earnings_growth_pct"]), 2),
        international_earnings_growth_pct=round(float(current["international_earnings_growth_pct"]), 2),
        earnings_growth_gap_pct_points=round(gap, 2),
        narrative=narrative,
    )
    return result, history

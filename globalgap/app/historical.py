from __future__ import annotations

import pandas as pd

from globalgap.app.models import HistoricalAnalog, HistoricalAnalogSummary, ValuationGap


def analyze_historical_analogs(
    valuation_gap: ValuationGap,
    valuation_history: pd.DataFrame,
    analog_count: int = 3,
) -> HistoricalAnalogSummary:
    history = valuation_history.iloc[:-1].copy()
    history["distance"] = (history["valuation_spread_ratio"] - valuation_gap.valuation_spread_ratio).abs()

    qualifying = history[history["valuation_spread_ratio"] >= valuation_gap.valuation_spread_ratio]
    if qualifying.empty:
        qualifying = history.nsmallest(analog_count, "distance")
    else:
        qualifying = qualifying.nsmallest(analog_count, "distance")

    analogs: list[HistoricalAnalog] = []
    for row in qualifying.itertuples(index=False):
        similarity_score = max(0.0, 100 - (float(row.distance) * 100))
        analogs.append(
            HistoricalAnalog(
                date=row.date.date().isoformat(),
                us_forward_pe=round(float(row.us_forward_pe), 2),
                international_forward_pe=round(float(row.international_forward_pe), 2),
                valuation_spread_ratio=round(float(row.valuation_spread_ratio), 4),
                following_5y_intl_minus_us_ann_pct=round(float(row.next_5y_intl_minus_us_ann_pct), 2),
                similarity_score=round(similarity_score, 2),
            )
        )

    avg_outperformance = sum(item.following_5y_intl_minus_us_ann_pct for item in analogs) / len(analogs)
    narrative = (
        f"In the {len(analogs)} historical periods with similarly wide valuation gaps, "
        f"international equities outperformed US equities by an average of {avg_outperformance:.1f}% annually over the following five years."
    )
    return HistoricalAnalogSummary(
        average_following_5y_outperformance_pct=round(avg_outperformance, 2),
        analog_count=len(analogs),
        analogs=analogs,
        narrative=narrative,
    )

from __future__ import annotations

from globalgap.app.models import (
    DollarCycle,
    EarningsGrowthGap,
    HistoricalAnalogSummary,
    PortfolioExposureSummary,
    RecommendationSummary,
    SimulationSummary,
    ValuationGap,
)
from globalgap.app.simulation import suggest_diversification_adjustment


def build_recommendation(
    exposure: PortfolioExposureSummary,
    valuation_gap: ValuationGap,
    earnings_gap: EarningsGrowthGap,
    dollar_cycle: DollarCycle,
    analogs: HistoricalAnalogSummary,
    simulation: SimulationSummary,
) -> RecommendationSummary:
    adjustment = suggest_diversification_adjustment(exposure)
    headline = (
        f"Your portfolio is {exposure.portfolio_us_weight * 100:.0f}% US equities and "
        f"{exposure.portfolio_international_weight * 100:.0f}% international equities."
    )
    note = (
        f"International equities currently trade at a {valuation_gap.international_discount_pct:.1f}% discount to US equities. "
        f"The dollar regime is {dollar_cycle.regime.replace('_', ' ').lower()}, and historical analogs point to "
        f"{analogs.average_following_5y_outperformance_pct:.1f}% annualized international outperformance after similarly wide valuation gaps."
    )
    benefit = (
        f"Moving toward roughly {adjustment.suggested_international_weight * 100:.0f}% international exposure "
        f"would diversify away some home-country risk. In the sample return set, the diversified mix changed Sharpe ratio by "
        f"{simulation.sharpe_ratio_change:+.2f} and expected return by {simulation.expected_return_change_pct:+.2f} percentage points."
    )
    return RecommendationSummary(
        headline=headline,
        plain_english_note=note + " " + earnings_gap.narrative,
        suggested_adjustment=adjustment,
        diversification_benefit_note=benefit,
    )

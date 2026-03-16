from __future__ import annotations

from typing import Optional

from value_check.app.config import DEFAULT_LOOKBACK_YEARS
from value_check.app.models import ValueCheckResult
from value_check.app.providers.base import ValuationDataProvider
from value_check.app.providers.valuation_provider import LocalValuationProvider
from value_check.app.services.expectations import build_implied_expectations
from value_check.app.services.history import compare_against_history
from value_check.app.services.interpretation import build_long_term_interpretation
from value_check.app.services.peers import compare_against_peers
from value_check.app.services.ratios import calculate_current_metrics
from value_check.app.services.scoring import compute_composite_score
from value_check.app.services.verdict import build_verdict


class ValueCheckAnalyzer:
    def __init__(self, provider: Optional[ValuationDataProvider] = None) -> None:
        self.provider = provider or LocalValuationProvider()

    def analyze(
        self,
        ticker: str,
        *,
        lookback_years: int = DEFAULT_LOOKBACK_YEARS,
        treasury_yield: Optional[float] = None,
        peer_group: Optional[str] = None,
    ) -> ValueCheckResult:
        snapshot = self.provider.get_snapshot(ticker)
        effective_treasury = treasury_yield if treasury_yield is not None else (snapshot.current_treasury_yield or self.provider.get_treasury_yield())
        current_metrics, caveats = calculate_current_metrics(snapshot, effective_treasury)
        history_df = self.provider.get_history(snapshot.ticker)
        peer_df = self.provider.get_peers(snapshot.ticker, peer_group=peer_group)
        history_rows = compare_against_history(current_metrics, history_df, lookback_years)
        peer_group_name = peer_group or snapshot.peer_group or f"{snapshot.sector} peers"
        peer_rows = compare_against_peers(current_metrics, peer_df, peer_group_name)
        composite_score, confidence_score, reasons = compute_composite_score(history_rows, peer_rows, current_metrics)
        verdict = build_verdict(composite_score, reasons, confidence_score)
        implied_expectations = build_implied_expectations(current_metrics, history_rows)
        long_term_takeaway, watch_items, caution_flags, summary = build_long_term_interpretation(
            ticker=snapshot.ticker,
            asset_type=snapshot.asset_type,
            verdict_label=str(verdict["label"]),
            current_metrics=current_metrics,
            peer_rows=peer_rows,
            caveats=caveats,
        )
        caveat_list = list(dict.fromkeys(caveats + caution_flags))

        return ValueCheckResult(
            ticker=snapshot.ticker,
            company_name=snapshot.company_name,
            asset_type=snapshot.asset_type,
            sector=snapshot.sector,
            industry=snapshot.industry,
            current_metrics={key: (round(value, 6) if isinstance(value, float) else value) for key, value in current_metrics.items()},
            historical_comparison=history_rows,
            peer_comparison=peer_rows,
            treasury_context={
                "treasury_yield": round(float(effective_treasury), 6),
                "fcf_spread": None if current_metrics["treasury_relative_fcf_spread"] is None else round(float(current_metrics["treasury_relative_fcf_spread"]), 6),
            },
            composite_score=composite_score,
            confidence_score=confidence_score,
            verdict=verdict,
            implied_expectations_summary=implied_expectations,
            long_term_takeaway=long_term_takeaway,
            watch_items=watch_items,
            caveats=caveat_list,
            plain_english_summary=summary,
            visualization_data={
                "percentile_bar_chart_data": history_rows,
                "peer_comparison_bar_chart_data": peer_rows,
                "valuation_scorecard_data": {
                    "composite_score": composite_score,
                    "confidence_score": confidence_score,
                },
                "treasury_spread_card_data": {
                    "fcf_yield": current_metrics["fcf_yield"],
                    "treasury_yield": effective_treasury,
                    "spread": current_metrics["treasury_relative_fcf_spread"],
                },
            },
        )

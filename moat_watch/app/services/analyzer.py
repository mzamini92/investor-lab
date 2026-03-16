from __future__ import annotations

import pandas as pd

from moat_watch.app.config import DEFAULT_QUARTER
from moat_watch.app.models import CommentaryRecord, MoatAnalysisResult, QuarterlyMetrics, WatchlistItem, WatchlistQuarterResult
from moat_watch.app.providers.base import MoatDataProvider
from moat_watch.app.providers.moat_provider import LocalMoatProvider
from moat_watch.app.services.alerts import build_alerts
from moat_watch.app.services.commentary import analyze_commentary
from moat_watch.app.services.interpretation import build_interpretation
from moat_watch.app.services.normalization import build_quarter_context, find_reference_rows
from moat_watch.app.services.peers import compare_against_peers
from moat_watch.app.services.scoring import compute_moat_score, score_change
from moat_watch.app.services.signals import build_signals
from moat_watch.app.services.trend import build_history_table, build_transition_label, consecutive_negative_streak


class MoatWatchAnalyzer:
    def __init__(self, provider: MoatDataProvider | None = None) -> None:
        self.provider = provider or LocalMoatProvider()

    def _row_to_metrics(self, row: pd.Series) -> QuarterlyMetrics:
        payload = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items() if k != "quarter_label" and k != "quarter_sort"}
        return QuarterlyMetrics(**payload)

    def _compute_analysis(
        self,
        current: QuarterlyMetrics,
        prior_quarter: QuarterlyMetrics | None,
        prior_year_quarter: QuarterlyMetrics | None,
        peer_df: pd.DataFrame,
        commentary: CommentaryRecord | None,
        score_history: list[dict[str, object]],
    ) -> MoatAnalysisResult:
        context = build_quarter_context(current, prior_quarter, prior_year_quarter)
        commentary_findings = analyze_commentary(commentary)
        signal_objects = build_signals(context, commentary_findings)
        signal_rows = [signal.__dict__ for signal in signal_objects]
        moat_score, moat_label, component_scores, confidence = compute_moat_score(signal_objects)
        peer_comparison = compare_against_peers(context, peer_df)

        prior_score = score_history[-2]["moat_health_score"] if len(score_history) >= 2 else None
        prior_label = score_history[-2]["moat_health_label"] if len(score_history) >= 2 else None
        current_history_row = {"quarter": current.quarter_label, "moat_health_score": moat_score, "moat_health_label": moat_label}
        score_history[-1] = current_history_row
        yoy_row = next((row for row in reversed(score_history[:-1]) if row["quarter"].endswith(f"Q{current.fiscal_quarter}") and not row["quarter"].startswith(str(current.fiscal_year))), None)
        transition_label = build_transition_label(moat_score, prior_score, moat_label, prior_label)

        history_df = self.provider.get_company_history(current.ticker).copy()
        history_df = history_df.loc[
            (history_df["fiscal_year"] * 10 + history_df["fiscal_quarter"]) <= (current.fiscal_year * 10 + current.fiscal_quarter)
        ].copy()
        history_df["gross_margin"] = pd.to_numeric(history_df["gross_profit"], errors="coerce") / pd.to_numeric(history_df["revenue"], errors="coerce")
        history_df["roic_wacc_spread"] = pd.to_numeric(history_df["roic"], errors="coerce") - pd.to_numeric(history_df["estimated_wacc"], errors="coerce")
        history_df["gross_margin_change_bps_qoq"] = history_df["gross_margin"].diff() * 10000.0
        history_df["roic_spread_change_qoq"] = history_df["roic_wacc_spread"].diff()
        streaks = {
            "gross_margin_compression": consecutive_negative_streak(history_df, "gross_margin_change_bps_qoq", threshold=0.0),
            "roic_spread_narrowing": consecutive_negative_streak(history_df, "roic_spread_change_qoq", threshold=0.0),
        }
        alerts, caution = build_alerts(
            moat_label=moat_label,
            transition_label=transition_label,
            signal_breakdown=signal_rows,
            commentary_findings=commentary_findings,
            streaks=streaks,
        )
        short_verdict, takeaway, watch_items, plain_summary = build_interpretation(
            ticker=current.ticker,
            moat_label=moat_label,
            moat_score=moat_score,
            transition_label=transition_label,
            signal_breakdown=signal_rows,
            commentary_findings=commentary_findings,
            peer_comparison=peer_comparison,
        )
        return MoatAnalysisResult(
            ticker=current.ticker,
            company_name=current.company_name,
            fiscal_quarter=current.quarter_label,
            fiscal_year=int(current.fiscal_year),
            moat_health_score=moat_score,
            moat_health_label=moat_label,
            score_change_qoq=score_change(moat_score, prior_score),
            score_change_yoy=score_change(moat_score, yoy_row["moat_health_score"] if yoy_row else None),
            signal_breakdown=signal_rows,
            peer_comparison=peer_comparison,
            transition_label=transition_label,
            alert_flags=alerts,
            commentary_findings=commentary_findings,
            caution_heuristic=caution,
            short_verdict=short_verdict,
            long_term_takeaway=takeaway,
            watch_items=watch_items,
            plain_english_summary=plain_summary,
            historical_moat_scores=build_history_table(score_history),
            visualization_data={
                "moat_score_history_chart_data": score_history,
                "signal_radar_data": signal_rows,
                "peer_comparison_bar_data": peer_comparison,
                "dashboard_card_data": {
                    "moat_health_score": moat_score,
                    "moat_health_label": moat_label,
                    "confidence_score": confidence,
                },
                "component_scores": component_scores,
            },
        )

    def analyze(self, ticker: str, quarter: str = DEFAULT_QUARTER) -> MoatAnalysisResult:
        history_df = self.provider.get_company_history(ticker)
        history_scores: list[dict[str, object]] = []
        ordered = history_df.sort_values(["fiscal_year", "fiscal_quarter"]).reset_index(drop=True)
        target_current: QuarterlyMetrics | None = None
        target_prior: QuarterlyMetrics | None = None
        target_yoy: QuarterlyMetrics | None = None
        target_history_scores: list[dict[str, object]] | None = None

        for _, row in ordered.iterrows():
            current = self._row_to_metrics(row)
            _, prior_row, prior_yoy_row = find_reference_rows(history_df, current.quarter_label)
            prior_quarter = self._row_to_metrics(prior_row) if prior_row is not None else None
            prior_yoy = self._row_to_metrics(prior_yoy_row) if prior_yoy_row is not None else None
            context = build_quarter_context(current, prior_quarter, prior_yoy)
            commentary_findings = analyze_commentary(self.provider.get_commentary(current.ticker, current.quarter_label))
            signal_rows = build_signals(context, commentary_findings)
            score, label, _, _ = compute_moat_score(signal_rows)
            history_scores.append({"quarter": current.quarter_label, "moat_health_score": score, "moat_health_label": label})
            if current.quarter_label.upper() == quarter.upper():
                target_current = current
                target_prior = prior_quarter
                target_yoy = prior_yoy
                target_history_scores = [item.copy() for item in history_scores]

        if target_current is None or target_history_scores is None:
            raise ValueError(f"Quarter {quarter} not found for {ticker}.")

        peer_df = self.provider.get_peer_quarter_data(target_current.ticker, target_current.quarter_label)
        commentary = self.provider.get_commentary(target_current.ticker, target_current.quarter_label)
        return self._compute_analysis(target_current, target_prior, target_yoy, peer_df, commentary, target_history_scores)

    def analyze_from_inputs(
        self,
        current: QuarterlyMetrics,
        *,
        prior_quarter: QuarterlyMetrics | None = None,
        prior_year_quarter: QuarterlyMetrics | None = None,
        peer_metrics: list[QuarterlyMetrics] | None = None,
        commentary: CommentaryRecord | None = None,
    ) -> MoatAnalysisResult:
        history_scores = [{"quarter": current.quarter_label, "moat_health_score": 50.0, "moat_health_label": "Yellow"}]
        peer_df = pd.DataFrame([metric.__dict__ | {"quarter_label": metric.quarter_label} for metric in (peer_metrics or [])])
        return self._compute_analysis(current, prior_quarter, prior_year_quarter, peer_df, commentary, history_scores)

    def analyze_watchlist(self, watchlist: list[WatchlistItem], quarter: str = DEFAULT_QUARTER) -> WatchlistQuarterResult:
        analyses = [self.analyze(item.ticker, quarter).to_dict() for item in watchlist]
        alert_digest = [
            f"{analysis['ticker']}: {analysis['moat_health_label']} - {analysis['transition_label'].replace('_', ' ')}"
            for analysis in analyses
            if analysis["alert_flags"]
        ]
        summary = {
            "quarter": quarter,
            "tracked_companies": len(analyses),
            "strong_green_count": sum(1 for row in analyses if row["moat_health_label"] == "Strong Green"),
            "yellow_or_worse_count": sum(1 for row in analyses if row["moat_health_label"] in {"Yellow", "Orange", "Red"}),
            "top_alerts": alert_digest[:5],
        }
        return WatchlistQuarterResult(
            quarter=quarter,
            analyses=analyses,
            alert_digest=alert_digest,
            summary=summary,
        )

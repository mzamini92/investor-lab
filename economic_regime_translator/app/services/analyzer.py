from __future__ import annotations

from dataclasses import fields
from typing import Optional

import pandas as pd

from economic_regime_translator.app.models import MacroSnapshot, RegimeAnalysisResult, SnapshotComparisonResult
from economic_regime_translator.app.services.analogs import find_historical_analogs
from economic_regime_translator.app.services.classification import classify_regime
from economic_regime_translator.app.services.interpretation import build_plain_english_summary
from economic_regime_translator.app.services.normalization import normalize_snapshot
from economic_regime_translator.app.services.portfolio_implications import build_portfolio_implications
from economic_regime_translator.app.services.scoring import build_scorecard, compute_confidence
from economic_regime_translator.app.services.transition import compare_regimes


class EconomicRegimeAnalyzer:
    @staticmethod
    def snapshot_from_history_row(row: pd.Series) -> MacroSnapshot:
        allowed_fields = {field.name for field in fields(MacroSnapshot)}
        payload = {}
        for key in row.index:
            if key not in allowed_fields or pd.isna(row[key]):
                continue
            value = row[key]
            if hasattr(value, "item"):
                try:
                    value = value.item()
                except Exception:  # noqa: BLE001
                    pass
            payload[key] = value
        payload["observation_date"] = str(payload["observation_date"])
        return MacroSnapshot(**payload)

    def latest_snapshot_from_history(self, history_df: pd.DataFrame) -> MacroSnapshot:
        ordered = history_df.copy()
        ordered["observation_date"] = pd.to_datetime(ordered["observation_date"])
        latest_row = ordered.sort_values("observation_date").iloc[-1]
        latest_row["observation_date"] = latest_row["observation_date"].date().isoformat()
        return self.snapshot_from_history_row(latest_row)

    def prior_snapshot_from_history(self, history_df: pd.DataFrame) -> MacroSnapshot:
        ordered = history_df.copy()
        ordered["observation_date"] = pd.to_datetime(ordered["observation_date"])
        if len(ordered.index) < 2:
            return self.latest_snapshot_from_history(history_df)
        prior_row = ordered.sort_values("observation_date").iloc[-2]
        prior_row["observation_date"] = prior_row["observation_date"].date().isoformat()
        return self.snapshot_from_history_row(prior_row)

    def classify(self, current_snapshot: MacroSnapshot, history_df: Optional[pd.DataFrame] = None) -> RegimeAnalysisResult:
        indicator_states = normalize_snapshot(current_snapshot)
        scorecard = build_scorecard(current_snapshot, indicator_states)
        classification = classify_regime(indicator_states, scorecard)
        confidence = compute_confidence(scorecard, classification["regime_label"])
        analogs = find_historical_analogs(current_snapshot, history_df if history_df is not None else pd.DataFrame())
        portfolio_implications = build_portfolio_implications(classification["regime_label"])
        plain_english = build_plain_english_summary(
            regime_label=classification["regime_label"],
            confidence_score=confidence,
            indicator_states=indicator_states,
            scorecard=scorecard,
            classification=classification,
            analogs=analogs,
            portfolio_implications=portfolio_implications,
        )
        visualization_data = {
            "indicator_score_table": [{"name": key, "value": value} for key, value in scorecard.items()],
            "regime_dashboard_summary": {
                "regime_label": classification["regime_label"],
                "confidence_score": confidence,
                "top_driver": classification["primary_drivers"][0],
            },
            "subscore_chart_data": [{"score": key, "value": value} for key, value in scorecard.items()],
            "historical_analog_table": analogs,
        }
        return RegimeAnalysisResult(
            observation_date=current_snapshot.observation_date,
            regime_label=classification["regime_label"],
            sub_regime_labels=classification["sub_regime_labels"],
            confidence_score=confidence,
            scorecard=scorecard,
            indicator_states=indicator_states,
            primary_drivers=classification["primary_drivers"],
            changed_signals=[],
            historical_analogs=analogs,
            portfolio_implications=portfolio_implications,
            risk_flags=classification["risk_flags"],
            watch_items=classification["watch_items"],
            plain_english_summary=plain_english,
            visualization_data=visualization_data,
        )

    def compare(
        self,
        current_snapshot: MacroSnapshot,
        prior_snapshot: MacroSnapshot,
        history_df: Optional[pd.DataFrame] = None,
    ) -> SnapshotComparisonResult:
        current = self.classify(current_snapshot, history_df)
        prior = self.classify(prior_snapshot, history_df)
        transition = compare_regimes(current.to_dict(), prior.to_dict())
        current_payload = current.to_dict()
        prior_payload = prior.to_dict()
        current_payload["changed_signals"] = [row["score"] for row in transition["changed_indicators"]]

        return SnapshotComparisonResult(
            prior_regime_label=prior.regime_label,
            current_regime_label=current.regime_label,
            transition_label=transition["transition_label"],
            transition_summary=transition["transition_summary"],
            changed_indicators=transition["changed_indicators"],
            strongest_positive_shift=transition["strongest_positive_shift"],
            strongest_negative_shift=transition["strongest_negative_shift"],
            current_analysis=current_payload,
            prior_analysis=prior_payload,
        )

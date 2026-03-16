import json
from pathlib import Path

import pandas as pd

from economic_regime_translator.app.config import DEFAULT_CURRENT_SNAPSHOT_FILE, DEFAULT_HISTORY_FILE, DEFAULT_PRIOR_SNAPSHOT_FILE
from economic_regime_translator.app.models import MacroSnapshot
from economic_regime_translator.app.services.analyzer import EconomicRegimeAnalyzer


def test_transition_analysis_detects_change() -> None:
    analyzer = EconomicRegimeAnalyzer()
    current = MacroSnapshot(**json.loads(Path(DEFAULT_CURRENT_SNAPSHOT_FILE).read_text(encoding="utf-8")))
    prior = MacroSnapshot(**json.loads(Path(DEFAULT_PRIOR_SNAPSHOT_FILE).read_text(encoding="utf-8")))
    history = pd.read_csv(DEFAULT_HISTORY_FILE)
    result = analyzer.compare(current, prior, history)
    assert result.current_regime_label
    assert result.prior_regime_label
    assert result.transition_label in {"regime_transition", "meaningful_improvement", "meaningful_deterioration", "unchanged"}
    assert len(result.changed_indicators) > 0


def test_latest_snapshot_from_history_helper() -> None:
    analyzer = EconomicRegimeAnalyzer()
    history = pd.read_csv(DEFAULT_HISTORY_FILE)
    latest = analyzer.latest_snapshot_from_history(history)
    prior = analyzer.prior_snapshot_from_history(history)
    assert latest.observation_date == "2025-11-30"
    assert prior.observation_date == "2024-08-31"

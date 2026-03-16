import pandas as pd

from moat_watch.app.services.trend import build_transition_label, consecutive_negative_streak


def test_transition_label_detects_deterioration() -> None:
    assert build_transition_label(48, 61, "Orange", "Green") == "clear deterioration"


def test_negative_streak_counts_recent_weakness() -> None:
    history_df = pd.DataFrame({"gross_margin_change_bps_qoq": [50, -20, -30, -10]})
    assert consecutive_negative_streak(history_df, "gross_margin_change_bps_qoq") == 3

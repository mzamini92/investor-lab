from globalgap.app.historical import analyze_historical_analogs
from globalgap.app.valuation import analyze_valuation_gap


def test_historical_analogs_return_rows() -> None:
    gap, history = analyze_valuation_gap()
    summary = analyze_historical_analogs(gap, history)
    assert summary.analog_count >= 1
    assert len(summary.analogs) == summary.analog_count

from globalgap.app.dollar_cycle import analyze_dollar_cycle


def test_dollar_cycle_returns_known_regime() -> None:
    result, _history = analyze_dollar_cycle()
    assert result.regime in {"STRONG_DOLLAR", "PEAK_DOLLAR", "WEAKENING_DOLLAR", "WEAK_DOLLAR"}
    assert 0 <= result.dxy_percentile_10y <= 100

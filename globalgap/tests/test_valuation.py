from globalgap.app.valuation import analyze_valuation_gap


def test_valuation_gap_shows_us_premium() -> None:
    gap, _history = analyze_valuation_gap()
    assert gap.us_forward_pe > gap.international_forward_pe
    assert gap.us_premium_pct > 0
    assert gap.international_discount_pct > 0

from value_check.app.services.scoring import compute_composite_score


def test_composite_score_moves_higher_when_signals_are_rich() -> None:
    historical_rows = [
        {"metric": "pe_ratio", "percentile_rank": 92.0},
        {"metric": "ps_ratio", "percentile_rank": 88.0},
        {"metric": "fcf_yield", "percentile_rank": 82.0},
    ]
    peer_rows = [
        {"metric": "pe_ratio", "premium_discount_vs_peer_median": 0.30},
        {"metric": "ps_ratio", "premium_discount_vs_peer_median": 0.25},
    ]
    current_metrics = {"treasury_relative_fcf_spread": -0.03}

    score, confidence, reasons = compute_composite_score(historical_rows, peer_rows, current_metrics)

    assert score > 80
    assert confidence >= 80
    assert any("premium" in reason.lower() or "rich" in reason.lower() for reason in reasons)


def test_composite_score_defaults_when_metric_coverage_is_sparse() -> None:
    score, confidence, reasons = compute_composite_score([], [], {"treasury_relative_fcf_spread": None})

    assert score == 50.0
    assert confidence == 35.0
    assert reasons

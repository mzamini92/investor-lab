from moat_watch.app.services.signals import build_signals


def test_pricing_power_signal_strengthens_with_positive_inputs() -> None:
    context = {
        "gross_margin_change_bps_qoq": 80.0,
        "roic_spread_change_qoq": 0.01,
        "roic_wacc_spread": 0.18,
        "price_realization": 0.04,
        "volume_growth": 0.03,
        "same_store_sales": 0.05,
        "asp_change_qoq": 0.02,
        "market_share_change_qoq": 0.01,
        "r_and_d_as_pct_revenue": 0.12,
        "r_and_d_intensity_change_qoq": 0.01,
        "sales_efficiency_proxy": 3.5,
        "sales_efficiency_change_qoq": 0.2,
    }
    commentary = {"pressure_score": 72.0}
    signals = [signal.__dict__ for signal in build_signals(context, commentary)]
    pricing = next(item for item in signals if item["signal_name"] == "pricing_power")
    assert pricing["strength_score"] > 65
    assert pricing["current_status"] == "pricing power intact"

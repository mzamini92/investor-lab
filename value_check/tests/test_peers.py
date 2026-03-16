from value_check.app.providers.valuation_provider import LocalValuationProvider
from value_check.app.services.peers import compare_against_peers
from value_check.app.services.ratios import calculate_current_metrics


def test_peer_provider_enriches_rows_with_metrics() -> None:
    provider = LocalValuationProvider()
    peer_df = provider.get_peers("MSFT")

    assert "pe_ratio" in peer_df.columns
    assert peer_df["ticker"].str.upper().isin(["AAPL", "NVDA", "AMZN", "GOOGL", "META"]).any()


def test_peer_comparison_returns_premium_discount() -> None:
    provider = LocalValuationProvider()
    snapshot = provider.get_snapshot("MSFT")
    current_metrics, _ = calculate_current_metrics(snapshot, treasury_yield=0.042)
    peer_rows = compare_against_peers(current_metrics, provider.get_peers("MSFT"), "Mega Cap Tech")

    pe_row = next(row for row in peer_rows if row["metric"] == "pe_ratio")
    assert pe_row["peer_median"] is not None
    assert pe_row["premium_discount_vs_peer_median"] is not None

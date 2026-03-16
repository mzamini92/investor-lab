from value_check.app.models import ValuationSnapshot
from value_check.app.services.ratios import calculate_current_metrics


def test_calculate_current_metrics_for_profitable_stock() -> None:
    snapshot = ValuationSnapshot(
        ticker="MSFT",
        company_name="Microsoft Corporation",
        asset_type="stock",
        sector="Technology",
        industry="Software",
        market_cap=3200.0,
        enterprise_value=3300.0,
        price=430.0,
        shares_outstanding=7.4,
        net_income_ttm=95.0,
        ebitda_ttm=140.0,
        revenue_ttm=245.0,
        free_cash_flow_ttm=70.0,
        book_value=206.0,
    )

    metrics, caveats = calculate_current_metrics(snapshot, treasury_yield=0.042)

    assert round(float(metrics["pe_ratio"]), 4) == 33.6842
    assert round(float(metrics["ev_ebitda"]), 4) == 23.5714
    assert round(float(metrics["ps_ratio"]), 4) == 13.0612
    assert round(float(metrics["pb_ratio"]), 4) == 15.5340
    assert round(float(metrics["fcf_yield"]), 6) == 0.021875
    assert round(float(metrics["treasury_relative_fcf_spread"]), 6) == -0.020125
    assert caveats == []


def test_invalid_metrics_create_caveats() -> None:
    snapshot = ValuationSnapshot(
        ticker="SNOW",
        company_name="Snowflake Inc.",
        asset_type="stock",
        sector="Technology",
        industry="Software",
        market_cap=65.0,
        enterprise_value=60.0,
        price=195.0,
        shares_outstanding=0.33,
        net_income_ttm=-1.1,
        ebitda_ttm=-0.3,
        revenue_ttm=3.2,
        free_cash_flow_ttm=-0.1,
        book_value=6.2,
    )

    metrics, caveats = calculate_current_metrics(snapshot, treasury_yield=0.042)

    assert metrics["pe_ratio"] is None
    assert metrics["ev_ebitda"] is None
    assert metrics["fcf_yield"] < 0
    assert any("negative" in caveat.lower() for caveat in caveats)

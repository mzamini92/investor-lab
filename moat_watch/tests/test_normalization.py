from moat_watch.app.models import QuarterlyMetrics
from moat_watch.app.services.normalization import build_quarter_context


def test_gross_margin_and_roic_spread_calculations() -> None:
    current = QuarterlyMetrics(
        ticker="AAA",
        company_name="Alpha",
        sector="Tech",
        industry="Software",
        fiscal_year=2025,
        fiscal_quarter=2,
        revenue=100.0,
        gross_profit=70.0,
        operating_margin=0.30,
        free_cash_flow=20.0,
        invested_capital=80.0,
        roic=0.24,
        estimated_wacc=0.09,
        r_and_d_expense=12.0,
        sales_and_marketing_expense=15.0,
        capex=4.0,
    )
    prior = QuarterlyMetrics(
        ticker="AAA",
        company_name="Alpha",
        sector="Tech",
        industry="Software",
        fiscal_year=2025,
        fiscal_quarter=1,
        revenue=100.0,
        gross_profit=68.0,
        operating_margin=0.29,
        free_cash_flow=19.0,
        invested_capital=79.0,
        roic=0.22,
        estimated_wacc=0.09,
        r_and_d_expense=11.0,
        sales_and_marketing_expense=15.0,
        capex=4.0,
    )
    context = build_quarter_context(current, prior, None)

    assert context["gross_margin"] == 0.70
    assert round(float(context["gross_margin_change_bps_qoq"]), 1) == 200.0
    assert round(float(context["roic_wacc_spread"]), 4) == 0.15

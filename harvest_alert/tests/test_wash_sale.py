from harvest_alert.app.models import Account, ReplacementSecurity, Transaction
from harvest_alert.app.services.wash_sale import screen_wash_sale_conflicts


def test_detects_recent_ira_buy_conflict() -> None:
    result = screen_wash_sale_conflicts(
        ticker="QQQ",
        proposed_sale_date="2026-03-15",
        transactions=[Transaction("ira_main", "2026-03-01", "QQQ", "buy", 2, 450, 900, "buy")],
        accounts={"ira_main": Account("ira_main", "IRA", "ira", False)},
        replacement=ReplacementSecurity(
            ticker="ONEQ",
            security_name="ONEQ",
            asset_class="US Equity",
            region="US",
            market_cap_focus="Large",
            style="Growth",
            factor_tilt="Growth",
            sector_focus="Technology",
            expense_ratio=0.0021,
            benchmark_index="NASDAQ Composite",
            strategy_tags=["growth"],
        ),
    )
    assert result["wash_sale_risk_level"] == "high"

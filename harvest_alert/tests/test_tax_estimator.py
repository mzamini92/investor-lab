from harvest_alert.app.models import TaxAssumptions, TaxLot
from harvest_alert.app.services.tax_estimator import estimate_lot_benefit, estimate_trading_cost


def test_tax_savings_and_net_benefit() -> None:
    lot = TaxLot("taxable", "VEA", "lot1", "2024-01-01", 100, 54.2, 5420, 45.0, -920.0, "long_term")
    assumptions = TaxAssumptions(
        federal_short_term_rate=0.37,
        federal_long_term_rate=0.20,
        state_tax_rate=0.05,
    )
    result = estimate_lot_benefit(lot, assumptions)
    assert result["harvestable_loss"] == 920.0
    assert round(result["estimated_tax_savings"], 2) == 230.0
    assert result["net_estimated_benefit"] < result["estimated_tax_savings"]


def test_trading_cost_estimate() -> None:
    assumptions = TaxAssumptions(0.37, 0.20, trading_cost_bps=2, bid_ask_cost_bps=3, slippage_bps=2)
    assert estimate_trading_cost(10000, assumptions) == 7.0

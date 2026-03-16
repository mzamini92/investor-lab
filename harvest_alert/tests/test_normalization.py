from harvest_alert.app.models import Account, Position, TaxLot, Transaction
from harvest_alert.app.services.normalization import normalize_brokerage_data


def test_lot_loss_is_filled_when_missing() -> None:
    normalized = normalize_brokerage_data(
        accounts=[Account("taxable", "Taxable", "taxable_brokerage", True)],
        positions=[Position("taxable", "VEA", "Vanguard Developed Markets", "ETF", 10, 40, 400, 500, None)],
        lots=[TaxLot("taxable", "VEA", "lot1", "2025-01-01", 10, 50, None, 40, None, None)],
        transactions=[],
        scan_date="2026-03-15",
    )
    assert normalized["lots"][0].unrealized_gain_loss == -100.0
    assert normalized["lots"][0].short_term_or_long_term == "long_term"

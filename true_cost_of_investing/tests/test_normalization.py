from true_cost_of_investing.app.models import HoldingInput
from true_cost_of_investing.app.services.normalization import normalize_holdings


def test_normalization_and_blended_expense_ratio() -> None:
    holdings = [
        HoldingInput("VOO", 100, 0.0010, "ETF"),
        HoldingInput("QQQ", 300, 0.0020, "ETF"),
    ]
    normalized, metrics = normalize_holdings(holdings)
    weight_map = {item.ticker: item.weight for item in normalized}
    assert weight_map["VOO"] == 0.25
    assert weight_map["QQQ"] == 0.75
    assert round(metrics["blended_expense_ratio"], 6) == 0.00175

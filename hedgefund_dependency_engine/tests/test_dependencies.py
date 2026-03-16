import math

from hedgefund_dependency_engine.app.services.analyzer import HedgefundDependencyAnalyzer
from hedgefund_dependency_engine.tests.test_exposure import build_provider


def test_dependency_aggregation() -> None:
    result = HedgefundDependencyAnalyzer(build_provider()).analyze([{"ticker": "ETF1", "amount": 50}, {"ticker": "ETF2", "amount": 50}])
    dependency_map = {row["dependency_name"]: row["exposure"] for row in result.dependency_exposures}
    expected_ai = (0.4 * 0.8) + (0.2 * 0.0) + (0.4 * 0.1)
    assert math.isclose(dependency_map["ai_capex"], expected_ai, rel_tol=1e-9)
    assert dependency_map["industrial_capex"] > dependency_map["energy_prices"]

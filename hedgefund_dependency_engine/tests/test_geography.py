import math

from hedgefund_dependency_engine.app.services.analyzer import HedgefundDependencyAnalyzer
from hedgefund_dependency_engine.tests.test_exposure import build_provider


def test_country_and_region_aggregation() -> None:
    result = HedgefundDependencyAnalyzer(build_provider()).analyze([{"ticker": "ETF1", "amount": 60}, {"ticker": "ETF2", "amount": 40}])
    country_map = {row["name"]: row["exposure"] for row in result.country_exposures}
    region_map = {row["name"]: row["exposure"] for row in result.region_exposures}
    assert math.isclose(country_map["United States"], 0.68, rel_tol=1e-9)
    assert math.isclose(country_map["Germany"], 0.32, rel_tol=1e-9)
    assert math.isclose(region_map["North America"], 0.68, rel_tol=1e-9)
    assert math.isclose(region_map["Europe"], 0.32, rel_tol=1e-9)

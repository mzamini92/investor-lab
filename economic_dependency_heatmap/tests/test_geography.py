import math

from economic_dependency_heatmap.app.services.analyzer import EconomicDependencyAnalyzer
from economic_dependency_heatmap.tests.test_exposure import build_provider


def test_country_and_region_aggregation() -> None:
    result = EconomicDependencyAnalyzer(build_provider()).analyze([{"ticker": "ETF1", "amount": 60}, {"ticker": "ETF2", "amount": 40}])
    country_map = {row["name"]: row["exposure"] for row in result.country_exposure_table}
    region_map = {row["name"]: row["exposure"] for row in result.region_exposure_table}
    assert math.isclose(country_map["United States"], 0.68, rel_tol=1e-9)
    assert math.isclose(country_map["Germany"], 0.32, rel_tol=1e-9)
    assert math.isclose(region_map["North America"], 0.68, rel_tol=1e-9)
    assert math.isclose(region_map["Europe"], 0.32, rel_tol=1e-9)


def test_country_hhi_and_effective_count() -> None:
    result = EconomicDependencyAnalyzer(build_provider()).analyze([{"ticker": "ETF1", "amount": 60}, {"ticker": "ETF2", "amount": 40}])
    expected_hhi = (0.68 ** 2) + (0.32 ** 2)
    assert math.isclose(result.concentration_metrics["country"]["hhi"], expected_hhi, rel_tol=1e-6)
    assert math.isclose(result.concentration_metrics["country"]["effective_count"], 1 / expected_hhi, rel_tol=1e-6)

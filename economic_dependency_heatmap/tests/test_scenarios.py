import math

from economic_dependency_heatmap.tests.test_exposure import build_provider
from economic_dependency_heatmap.app.services.analyzer import EconomicDependencyAnalyzer


def test_scenario_impact_calculation() -> None:
    result = EconomicDependencyAnalyzer(build_provider()).analyze(
        [{"ticker": "ETF1", "amount": 50}, {"ticker": "ETF2", "amount": 50}],
        selected_scenarios=["ai_boom"],
    )
    scenario = result.scenario_impact_results[0]
    dependency_map = {row["dependency_name"]: row["contribution"] for row in scenario["top_contributing_dependencies"]}
    expected = ((0.4 * 0.8) + (0.4 * 0.1)) * 1.0
    expected += ((0.4 * 0.7) + (0.4 * 0.0)) * 0.5
    expected += ((0.4 * 0.9) + (0.4 * 0.0)) * 0.5
    assert math.isclose(scenario["estimated_portfolio_impact_score"], expected, rel_tol=1e-9)
    assert scenario["scenario_name"] == "ai_boom"

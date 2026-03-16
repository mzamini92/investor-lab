from economic_dependency_heatmap.tests.test_exposure import build_provider
from economic_dependency_heatmap.app.services.analyzer import EconomicDependencyAnalyzer


def test_warning_and_recommendation_generation() -> None:
    result = EconomicDependencyAnalyzer(build_provider()).analyze([{"ticker": "ETF1", "amount": 90}, {"ticker": "ETF2", "amount": 10}])
    warning_blob = " ".join(result.warnings)
    recommendation_blob = " ".join(result.recommendations)
    assert "portfolio" in warning_blob.lower() or "economic reality gap" in warning_blob.lower()
    assert recommendation_blob

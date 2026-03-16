from hedgefund_dependency_engine.app.services.analyzer import HedgefundDependencyAnalyzer
from hedgefund_dependency_engine.tests.test_exposure import build_provider


def test_warning_and_insight_generation() -> None:
    result = HedgefundDependencyAnalyzer(build_provider()).analyze([{"ticker": "ETF1", "amount": 90}, {"ticker": "ETF2", "amount": 10}])
    warnings = " ".join(result.warnings)
    insights = " ".join(result.summary_insights)
    assert "portfolio" in warnings.lower() or "graph" in warnings.lower()
    assert "macro" in insights.lower() or "dependency" in insights.lower()

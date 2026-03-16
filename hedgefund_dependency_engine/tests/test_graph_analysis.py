from hedgefund_dependency_engine.app.services.analyzer import HedgefundDependencyAnalyzer
from hedgefund_dependency_engine.tests.test_exposure import build_provider


def test_graph_construction_and_centrality() -> None:
    result = HedgefundDependencyAnalyzer(build_provider()).analyze([{"ticker": "ETF1", "amount": 50}, {"ticker": "ETF2", "amount": 50}])
    assert result.graph_data["nodes"]
    assert result.graph_data["edges"]
    company_nodes = result.graph_centrality["company"]
    assert company_nodes
    assert company_nodes[0]["label"] in {"AAA", "CCC", "BBB"}

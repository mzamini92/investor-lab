from harvest_alert.app.services.ranking import score_opportunity


def test_ranking_penalizes_wash_sale_risk() -> None:
    low_risk = score_opportunity(net_benefit=250, similarity_score=92, wash_sale_risk_level="none", drift_penalty=2)
    high_risk = score_opportunity(net_benefit=250, similarity_score=92, wash_sale_risk_level="high", drift_penalty=2)
    assert low_risk > high_risk

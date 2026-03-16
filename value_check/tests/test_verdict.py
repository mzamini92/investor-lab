from value_check.app.services.verdict import map_score_to_verdict


def test_verdict_label_mapping() -> None:
    assert map_score_to_verdict(10) == "cheap"
    assert map_score_to_verdict(30) == "slightly cheap"
    assert map_score_to_verdict(50) == "fair"
    assert map_score_to_verdict(65) == "slightly expensive"
    assert map_score_to_verdict(80) == "expensive"
    assert map_score_to_verdict(95) == "extremely expensive"

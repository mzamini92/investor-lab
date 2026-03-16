from moat_watch.app.models import SignalResult
from moat_watch.app.services.scoring import compute_moat_score, map_score_to_label


def test_moat_score_and_label_mapping() -> None:
    signals = [
        SignalResult("gross_margin_trajectory", "expanding", "improving", 80, "good"),
        SignalResult("roic_spread", "widening spread", "improving", 82, "good"),
        SignalResult("pricing_power", "pricing power intact", "improving", 78, "good"),
        SignalResult("market_share", "gaining share", "improving", 72, "good"),
        SignalResult("innovation_reinvestment", "reinvesting to extend moat", "improving", 70, "good"),
        SignalResult("sales_efficiency", "efficient customer economics", "improving", 68, "good"),
        SignalResult("commentary_pressure", "management tone supportive", "improving", 66, "good"),
    ]
    score, label, _, _ = compute_moat_score(signals)
    assert score > 70
    assert label in {"Green", "Strong Green"}
    assert map_score_to_label(32) == "Red"

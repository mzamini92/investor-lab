from moat_watch.app.models import CommentaryRecord
from moat_watch.app.services.commentary import analyze_commentary


def test_commentary_detection_finds_pressure_signals() -> None:
    findings = analyze_commentary(
        CommentaryRecord(
            ticker="SBUX",
            quarter="2025Q2",
            raw_commentary_text="We saw more promotions, rising price sensitivity, and a more competitive backdrop.",
            mentions_promotions=True,
            mentions_pricing_pressure=True,
            mentions_competition=True,
        )
    )
    assert findings["pressure_score"] < 50
    assert findings["negative_signals"]

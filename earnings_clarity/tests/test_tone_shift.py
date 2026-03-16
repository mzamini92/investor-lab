from earnings_clarity.app.services.parser import parse_raw_transcript
from earnings_clarity.app.services.tone_shift import compare_tone


def test_tone_shift_detects_more_cautious_language() -> None:
    prior = parse_raw_transcript("AAPL", "2025Q3", "CEO: We remain confident and demand is strong.")
    current = parse_raw_transcript("AAPL", "2025Q4", "CEO: We remain cautious. Visibility is limited and the environment is uncertain.")
    result = compare_tone(current, prior)
    assert result["tone_shift_label"] == "more_cautious"
    assert float(result["tone_shift_score"]) < 0

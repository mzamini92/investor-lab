from earnings_clarity.app.services.guidance import analyze_guidance_language
from earnings_clarity.app.services.parser import parse_raw_transcript


def test_guidance_detector_finds_caution_language() -> None:
    transcript = parse_raw_transcript(
        "AAPL",
        "2025Q4",
        """
        CEO: Demand was healthy overall.
        CFO: We remain cautious and visibility is limited. Margin pressure is still a headwind.
        Analyst: Are you lowering outlook?
        CFO: We are not assuming a broad recovery.
        """,
    )
    result = analyze_guidance_language(transcript, "Management stayed cautious.")
    assert result["guidance_label"] == "cautious"
    assert float(result["guidance_caution_score"]) > float(result["guidance_positive_score"])

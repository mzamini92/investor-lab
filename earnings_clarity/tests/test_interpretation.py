from earnings_clarity.app.services.interpretation import build_long_term_interpretation


def test_long_term_interpretation_returns_watch_items_and_status() -> None:
    result = build_long_term_interpretation(
        company_name="Apple",
        headline={"headline_classification": "beat"},
        guidance_view={"guidance_caution_score": 6.0, "guidance_positive_score": 2.0, "guidance_label": "cautious"},
        tone_shift={"tone_shift_label": "more_cautious"},
        top_topics=[{"topic": "china"}, {"topic": "services"}, {"topic": "margins"}],
    )
    assert result["thesis_status"] in {"mixed", "weakening"}
    assert "china" in result["next_quarter_watch_items"]

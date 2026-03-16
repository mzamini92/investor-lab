from harvest_alert.app.models import ReplacementSecurity
from harvest_alert.app.services.similarity import compute_similarity


def test_similarity_score_rewards_close_match() -> None:
    original = ReplacementSecurity("VTI", "VTI", "US Equity", "US", "All Cap", "Blend", None, None, 0.0003, "CRSP US Total Market", ["core", "broad"])
    replacement = ReplacementSecurity("ITOT", "ITOT", "US Equity", "US", "All Cap", "Blend", None, None, 0.0003, "S&P Total Market", ["core", "broad"], similar_to=["VTI"])
    score, summary, _ = compute_similarity(original, replacement)
    assert score > 80
    assert "low expected drift" in summary.lower()

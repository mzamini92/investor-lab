from harvest_alert.app.models import ReplacementSecurity
from harvest_alert.app.services.replacements import recommend_replacements


def test_recommends_similar_etf() -> None:
    universe = [
        ReplacementSecurity("VEA", "VEA", "International Equity", "Developed ex-US", "Large", "Blend", None, None, 0.0005, "FTSE Developed", ["developed", "international"]),
        ReplacementSecurity("IEFA", "IEFA", "International Equity", "Developed ex-US", "Large", "Blend", None, None, 0.0007, "MSCI EAFE IMI", ["developed", "international"], similar_to=["VEA"], holdings_similarity_score=0.94),
    ]
    rows = recommend_replacements("VEA", universe)
    assert rows
    assert rows[0]["ticker"] == "IEFA"

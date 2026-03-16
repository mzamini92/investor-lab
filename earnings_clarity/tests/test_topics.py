from earnings_clarity.app.services.parser import parse_raw_transcript
from earnings_clarity.app.services.topics import extract_topics


def test_topic_extraction_ranks_key_topics() -> None:
    transcript = parse_raw_transcript(
        "MSFT",
        "2025Q4",
        """
        CEO: AI demand remained strong across cloud workloads.
        CFO: Cloud demand was healthy and AI capex remained elevated.
        Analyst: How should we think about enterprise demand and pricing?
        """,
    )
    topics = extract_topics(transcript)
    topic_names = [item["topic"] for item in topics]
    assert "ai" in topic_names
    assert "cloud" in topic_names

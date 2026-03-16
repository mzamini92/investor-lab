from earnings_clarity.app.services.parser import parse_raw_transcript


RAW = """
Operator: Welcome everyone.
Jane Doe (CEO): Demand improved and services remained strong.
John Smith (CFO): We remain cautious on China and visibility is limited.
Operator: We will now begin the question-and-answer session.
Analyst: What changed this quarter?
Jane Doe (CEO): China was mixed and we are watching closely.
"""


def test_parser_segments_speakers_and_sections() -> None:
    transcript = parse_raw_transcript("TEST", "2025Q4", RAW)
    assert len(transcript.utterances) == 6
    assert transcript.utterances[1].speaker_role == "ceo"
    assert transcript.utterances[2].speaker_role == "cfo"
    assert transcript.utterances[3].section == "analyst_qna"

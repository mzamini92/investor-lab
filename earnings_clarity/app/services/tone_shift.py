from __future__ import annotations

from collections import Counter

from earnings_clarity.app.models import ToneShiftAnalysis, Transcript
from earnings_clarity.app.services.evidence import build_evidence_snippet
from earnings_clarity.app.utils.constants import CAUTIOUS_TONE_WORDS, POSITIVE_TONE_WORDS, TOPIC_KEYWORDS
from earnings_clarity.app.utils.text import normalize_text


def _tone_counts(transcript: Transcript) -> tuple[int, int]:
    positive = 0
    cautious = 0
    for utterance in transcript.utterances:
        lowered = normalize_text(utterance.text).lower()
        positive += sum(lowered.count(word) for word in POSITIVE_TONE_WORDS)
        cautious += sum(lowered.count(word) for word in CAUTIOUS_TONE_WORDS)
    return positive, cautious


def compare_tone(current: Transcript, prior: Transcript | None) -> dict[str, object]:
    if prior is None:
        return {
            "tone_shift_label": "similar",
            "tone_shift_score": 0.0,
            "changed_topics": [],
            "evidence": [],
        }

    curr_positive, curr_cautious = _tone_counts(current)
    prev_positive, prev_cautious = _tone_counts(prior)
    net_change = (curr_positive - curr_cautious) - (prev_positive - prev_cautious)
    label = "similar"
    if net_change >= 2:
        label = "more_positive"
    elif net_change <= -2:
        label = "more_cautious"

    curr_topics = Counter()
    prev_topics = Counter()
    for topic, keywords in TOPIC_KEYWORDS.items():
        curr_topics[topic] = sum(
            normalize_text(utterance.text).lower().count(keyword)
            for utterance in current.utterances
            for keyword in keywords
        )
        prev_topics[topic] = sum(
            normalize_text(utterance.text).lower().count(keyword)
            for utterance in prior.utterances
            for keyword in keywords
        )
    changed_topics = [
        topic
        for topic in TOPIC_KEYWORDS
        if abs(curr_topics[topic] - prev_topics[topic]) >= 2
    ][:5]

    evidence = []
    for utterance in current.utterances:
        lowered = normalize_text(utterance.text).lower()
        if label == "more_cautious" and any(word in lowered for word in CAUTIOUS_TONE_WORDS):
            evidence.append(build_evidence_snippet("tone_shift", utterance, 0.7))
        elif label == "more_positive" and any(word in lowered for word in POSITIVE_TONE_WORDS):
            evidence.append(build_evidence_snippet("tone_shift", utterance, 0.7))
    analysis = ToneShiftAnalysis(
        tone_shift_label=label,  # type: ignore[arg-type]
        tone_shift_score=round(float(net_change), 2),
        changed_topics=changed_topics,
        evidence=evidence[:5],
    )
    return {
        "tone_shift_label": analysis.tone_shift_label,
        "tone_shift_score": analysis.tone_shift_score,
        "changed_topics": analysis.changed_topics,
        "evidence": [
            {
                "claim": item.claim,
                "snippet": item.snippet,
                "speaker": item.speaker,
                "speaker_role": item.speaker_role,
                "section": item.section,
                "confidence": item.confidence,
            }
            for item in analysis.evidence
        ],
    }

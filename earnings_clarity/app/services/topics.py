from __future__ import annotations

from earnings_clarity.app.models import TopicSignal, Transcript
from earnings_clarity.app.services.evidence import build_evidence_snippet
from earnings_clarity.app.utils.constants import CAUTIOUS_TONE_WORDS, POSITIVE_TONE_WORDS, TOPIC_KEYWORDS
from earnings_clarity.app.utils.text import normalize_text


def extract_topics(transcript: Transcript) -> list[dict[str, object]]:
    topic_signals: list[TopicSignal] = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        mentions = 0
        management_mentions = 0
        analyst_mentions = 0
        snippets = []
        tone_score = 0
        for utterance in transcript.utterances:
            lowered = normalize_text(utterance.text).lower()
            hit_count = sum(lowered.count(keyword) for keyword in keywords)
            if hit_count <= 0:
                continue
            mentions += hit_count
            if utterance.speaker_role in {"ceo", "cfo", "executive"}:
                management_mentions += hit_count
            if utterance.speaker_role == "analyst":
                analyst_mentions += hit_count
            tone_score += sum(1 for word in POSITIVE_TONE_WORDS if word in lowered)
            tone_score -= sum(1 for word in CAUTIOUS_TONE_WORDS if word in lowered)
            snippets.append(build_evidence_snippet(f"topic:{topic}", utterance, 0.62))
        if mentions:
            tone = "balanced"
            if tone_score >= 2:
                tone = "positive"
            elif tone_score <= -2:
                tone = "cautious"
            topic_signals.append(
                TopicSignal(
                    topic=topic,
                    mentions=mentions,
                    management_mentions=management_mentions,
                    analyst_mentions=analyst_mentions,
                    tone=tone,
                    snippets=snippets[:4],
                )
            )
    topic_signals.sort(key=lambda item: (item.mentions, item.management_mentions), reverse=True)
    return [
        {
            "topic": signal.topic,
            "mentions": signal.mentions,
            "management_mentions": signal.management_mentions,
            "analyst_mentions": signal.analyst_mentions,
            "tone": signal.tone,
            "snippets": [
                {
                    "claim": snippet.claim,
                    "snippet": snippet.snippet,
                    "speaker": snippet.speaker,
                    "speaker_role": snippet.speaker_role,
                    "section": snippet.section,
                    "confidence": snippet.confidence,
                }
                for snippet in signal.snippets
            ],
        }
        for signal in topic_signals
    ]

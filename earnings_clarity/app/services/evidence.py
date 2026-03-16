from __future__ import annotations

from collections.abc import Iterable

from earnings_clarity.app.models import EvidenceSnippet, TranscriptUtterance
from earnings_clarity.app.utils.text import clip_text


def build_evidence_snippet(claim: str, utterance: TranscriptUtterance, confidence: float) -> EvidenceSnippet:
    return EvidenceSnippet(
        claim=claim,
        snippet=clip_text(utterance.text, 240),
        speaker=utterance.speaker,
        speaker_role=utterance.speaker_role,
        section=utterance.section,
        confidence=round(confidence, 2),
    )


def top_evidence(snippets: Iterable[EvidenceSnippet], limit: int = 8) -> list[dict[str, object]]:
    ranked = sorted(snippets, key=lambda snippet: snippet.confidence, reverse=True)
    return [
        {
            "claim": snippet.claim,
            "snippet": snippet.snippet,
            "speaker": snippet.speaker,
            "speaker_role": snippet.speaker_role,
            "section": snippet.section,
            "confidence": snippet.confidence,
        }
        for snippet in ranked[:limit]
    ]

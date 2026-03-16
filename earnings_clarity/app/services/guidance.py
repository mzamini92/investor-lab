from __future__ import annotations

from earnings_clarity.app.models import EvidenceSnippet, SignalDetection, Transcript
from earnings_clarity.app.services.evidence import build_evidence_snippet
from earnings_clarity.app.utils.constants import CAUTION_GUIDANCE_PHRASES, DEFENSIVE_QA_PHRASES, POSITIVE_GUIDANCE_PHRASES
from earnings_clarity.app.utils.text import normalize_text


def _scan_phrase_dict(transcript: Transcript, phrase_weights: dict[str, float], label: str) -> SignalDetection:
    snippets: list[EvidenceSnippet] = []
    score = 0.0
    count = 0
    for utterance in transcript.utterances:
        lowered = normalize_text(utterance.text).lower()
        for phrase, weight in phrase_weights.items():
            if phrase in lowered:
                score += weight
                count += lowered.count(phrase)
                snippets.append(build_evidence_snippet(label, utterance, min(0.95, 0.55 + (weight / 4.0))))
    return SignalDetection(label=label, score=round(score, 2), count=count, snippets=snippets[:10])


def analyze_guidance_language(transcript: Transcript, guidance_summary: str = "") -> dict[str, object]:
    positive = _scan_phrase_dict(transcript, POSITIVE_GUIDANCE_PHRASES, "positive_guidance")
    caution = _scan_phrase_dict(transcript, CAUTION_GUIDANCE_PHRASES, "caution_guidance")
    defensive = _scan_phrase_dict(transcript, DEFENSIVE_QA_PHRASES, "defensive_qna")
    guidance_text = guidance_summary.lower()
    if "raised" in guidance_text or "improved" in guidance_text:
        positive.score += 1.2
        positive.count += 1
    if "lowered" in guidance_text or "cautious" in guidance_text or "soft" in guidance_text:
        caution.score += 1.8
        caution.count += 1

    signal_label = "mixed"
    if caution.score - positive.score >= 1.5:
        signal_label = "cautious"
    elif positive.score - caution.score >= 1.5:
        signal_label = "positive"

    return {
        "guidance_label": signal_label,
        "guidance_caution_score": round(caution.score + (0.35 * defensive.score), 2),
        "guidance_positive_score": round(positive.score, 2),
        "defensive_qna_score": round(defensive.score, 2),
        "caution_signals": [
            {"label": caution.label, "score": caution.score, "count": caution.count},
            {"label": defensive.label, "score": defensive.score, "count": defensive.count},
        ],
        "positive_signals": [
            {"label": positive.label, "score": positive.score, "count": positive.count},
        ],
        "evidence": [*caution.snippets[:4], *positive.snippets[:4], *defensive.snippets[:3]],
    }

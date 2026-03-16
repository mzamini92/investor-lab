from __future__ import annotations

from typing import Optional

from earnings_clarity.app.models import EarningsCallAnalysis, EarningsEvent, Transcript, TranscriptUtterance
from earnings_clarity.app.providers.base import EarningsEventProvider, TranscriptProvider
from earnings_clarity.app.providers.earnings_provider import LocalEarningsEventProvider
from earnings_clarity.app.providers.transcript_provider import LocalTranscriptProvider
from earnings_clarity.app.services.evidence import top_evidence
from earnings_clarity.app.services.guidance import analyze_guidance_language
from earnings_clarity.app.services.headline_analysis import analyze_headline_result
from earnings_clarity.app.services.interpretation import build_long_term_interpretation
from earnings_clarity.app.services.summarizer import build_extended_summary, build_five_point_summary
from earnings_clarity.app.services.tone_shift import compare_tone
from earnings_clarity.app.services.topics import extract_topics


class EarningsClarityAnalyzer:
    def __init__(
        self,
        transcript_provider: Optional[TranscriptProvider] = None,
        earnings_provider: Optional[EarningsEventProvider] = None,
    ) -> None:
        self.transcript_provider = transcript_provider or LocalTranscriptProvider()
        self.earnings_provider = earnings_provider or LocalEarningsEventProvider()

    def analyze_call(
        self,
        *,
        earnings_event: EarningsEvent,
        transcript: Transcript,
        prior_transcript: Transcript | None = None,
    ) -> EarningsCallAnalysis:
        headline = analyze_headline_result(earnings_event)
        guidance_view = analyze_guidance_language(transcript, earnings_event.guidance_summary)
        topics = extract_topics(transcript)
        tone_shift = compare_tone(transcript, prior_transcript)

        caution_topic = next((topic for topic in topics if topic["tone"] == "cautious"), topics[0] if topics else None)
        risk_label = caution_topic["topic"] if caution_topic else "guidance / demand uncertainty"
        risk_flag = {
            "label": risk_label,
            "score": round(float(guidance_view["guidance_caution_score"]) + max(0.0, -float(tone_shift["tone_shift_score"])), 2),
        }

        interpretation = build_long_term_interpretation(
            company_name=earnings_event.company_name,
            headline=headline,
            guidance_view=guidance_view,
            tone_shift=tone_shift,
            top_topics=topics,
        )
        summary = build_five_point_summary(
            event=earnings_event,
            headline=headline,
            guidance_view=guidance_view,
            risk_flag=risk_flag,
            tone_shift=tone_shift,
            interpretation=interpretation,
        )
        extended = build_extended_summary(earnings_event, summary)

        evidence_pool = [
            *guidance_view["evidence"],
            *tone_shift["evidence"],
            *[snippet for topic in topics[:4] for snippet in topic["snippets"][:2]],
        ]
        confidence_score = min(
            0.95,
            0.45
            + (0.05 * len(guidance_view["evidence"]))
            + (0.03 * len(tone_shift["evidence"]))
            + (0.02 * len(topics)),
        )
        return EarningsCallAnalysis(
            ticker=earnings_event.ticker,
            company_name=earnings_event.company_name,
            quarter=earnings_event.quarter,
            headline_result=headline,
            guidance_view=guidance_view,
            risk_flag=risk_flag,
            tone_shift=tone_shift,
            long_term_takeaway=interpretation["long_term_takeaway"],
            thesis_status=interpretation["thesis_status"],
            confidence_score=round(confidence_score, 2),
            evidence_snippets=top_evidence(
                [
                    item
                    if not isinstance(item, dict)
                    else _dict_to_evidence(item)
                    for item in evidence_pool
                ],
                limit=10,
            ),
            detected_topics=topics,
            caution_signals=list(guidance_view["caution_signals"]),
            positive_signals=list(guidance_view["positive_signals"]),
            watch_items=list(interpretation["next_quarter_watch_items"]),
            five_point_summary=summary,
            extended_summary=extended,
            analysis_metadata={
                "prior_transcript_used": prior_transcript is not None,
                "current_transcript_utterance_count": len(transcript.utterances),
                "prior_transcript_utterance_count": 0 if prior_transcript is None else len(prior_transcript.utterances),
            },
        )

    def analyze_saved_call(self, ticker: str, quarter: str, prior_quarter: str | None = None) -> EarningsCallAnalysis:
        event = self.earnings_provider.get_earnings_event(ticker, quarter)
        transcript = self.transcript_provider.get_transcript(ticker, quarter)
        prior = None if not prior_quarter else self.transcript_provider.get_transcript(ticker, prior_quarter)
        return self.analyze_call(earnings_event=event, transcript=transcript, prior_transcript=prior)


def _dict_to_evidence(item: dict[str, object]):
    from earnings_clarity.app.models import EvidenceSnippet

    return EvidenceSnippet(
        claim=str(item["claim"]),
        snippet=str(item["snippet"]),
        speaker=str(item["speaker"]),
        speaker_role=str(item["speaker_role"]),  # type: ignore[arg-type]
        section=str(item["section"]),  # type: ignore[arg-type]
        confidence=float(item["confidence"]),
    )

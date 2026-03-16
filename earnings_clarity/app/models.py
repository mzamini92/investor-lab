from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from earnings_clarity.app.exceptions import ValidationError


SpeakerRole = Literal["ceo", "cfo", "executive", "analyst", "operator", "unknown"]
TranscriptSection = Literal["operator", "prepared_remarks", "analyst_qna", "closing", "unknown"]


@dataclass
class HoldingPosition:
    ticker: str
    shares: float

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        if not self.ticker:
            raise ValidationError("Holding ticker cannot be empty.")
        if self.shares <= 0:
            raise ValidationError(f"Shares must be positive for {self.ticker}.")


@dataclass
class EarningsEvent:
    ticker: str
    company_name: str
    quarter: str
    earnings_date: str
    revenue_actual: float
    revenue_estimate: float
    eps_actual: float
    eps_estimate: float
    guidance_summary: str = ""

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        self.company_name = self.company_name.strip()
        self.quarter = self.quarter.strip()
        self.earnings_date = self.earnings_date.strip()
        self.guidance_summary = self.guidance_summary.strip()
        if not self.ticker or not self.company_name or not self.quarter:
            raise ValidationError("Ticker, company_name, and quarter are required.")


@dataclass
class TranscriptUtterance:
    speaker: str
    speaker_role: SpeakerRole
    section: TranscriptSection
    text: str
    order: int

    def __post_init__(self) -> None:
        self.speaker = self.speaker.strip()
        self.text = self.text.strip()
        if not self.text:
            raise ValidationError("Transcript utterance text cannot be empty.")


@dataclass
class Transcript:
    ticker: str
    quarter: str
    utterances: list[TranscriptUtterance]
    source: str = "local"

    def __post_init__(self) -> None:
        self.ticker = self.ticker.upper().strip()
        self.quarter = self.quarter.strip()
        if not self.ticker or not self.quarter:
            raise ValidationError("Transcript ticker and quarter are required.")
        if not self.utterances:
            raise ValidationError(f"Transcript for {self.ticker} {self.quarter} is empty.")


@dataclass
class EvidenceSnippet:
    claim: str
    snippet: str
    speaker: str
    speaker_role: SpeakerRole
    section: TranscriptSection
    confidence: float


@dataclass
class SignalDetection:
    label: str
    score: float
    count: int
    snippets: list[EvidenceSnippet]


@dataclass
class TopicSignal:
    topic: str
    mentions: int
    management_mentions: int
    analyst_mentions: int
    tone: str
    snippets: list[EvidenceSnippet]


@dataclass
class ToneShiftAnalysis:
    tone_shift_label: Literal["more_positive", "similar", "more_cautious"]
    tone_shift_score: float
    changed_topics: list[str]
    evidence: list[EvidenceSnippet]


@dataclass
class EarningsCallAnalysis:
    ticker: str
    company_name: str
    quarter: str
    headline_result: dict[str, Any]
    guidance_view: dict[str, Any]
    risk_flag: dict[str, Any]
    tone_shift: dict[str, Any]
    long_term_takeaway: str
    thesis_status: str
    confidence_score: float
    evidence_snippets: list[dict[str, Any]]
    detected_topics: list[dict[str, Any]]
    caution_signals: list[dict[str, Any]]
    positive_signals: list[dict[str, Any]]
    watch_items: list[str]
    five_point_summary: list[str]
    extended_summary: dict[str, str]
    analysis_metadata: dict[str, Any] = field(
        default_factory=lambda: {"generated_at": datetime.now(timezone.utc).isoformat()}
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

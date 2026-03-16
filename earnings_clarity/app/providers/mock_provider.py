from __future__ import annotations

from earnings_clarity.app.models import EarningsEvent, Transcript
from earnings_clarity.app.providers.base import EarningsEventProvider, TranscriptProvider


class MockTranscriptProvider(TranscriptProvider):
    def __init__(self, transcripts: dict[tuple[str, str], Transcript]) -> None:
        self.transcripts = {(ticker.upper(), quarter): transcript for (ticker, quarter), transcript in transcripts.items()}

    def get_transcript(self, ticker: str, quarter: str) -> Transcript:
        return self.transcripts[(ticker.upper(), quarter)]


class MockEarningsEventProvider(EarningsEventProvider):
    def __init__(self, events: dict[tuple[str, str], EarningsEvent]) -> None:
        self.events = {(ticker.upper(), quarter): event for (ticker, quarter), event in events.items()}

    def get_earnings_event(self, ticker: str, quarter: str) -> EarningsEvent:
        return self.events[(ticker.upper(), quarter)]

    def list_events(self) -> list[EarningsEvent]:
        return list(self.events.values())

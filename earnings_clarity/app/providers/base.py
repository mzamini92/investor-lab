from __future__ import annotations

from abc import ABC, abstractmethod

from earnings_clarity.app.models import EarningsEvent, Transcript


class TranscriptProvider(ABC):
    @abstractmethod
    def get_transcript(self, ticker: str, quarter: str) -> Transcript:
        raise NotImplementedError


class EarningsEventProvider(ABC):
    @abstractmethod
    def get_earnings_event(self, ticker: str, quarter: str) -> EarningsEvent:
        raise NotImplementedError

    @abstractmethod
    def list_events(self) -> list[EarningsEvent]:
        raise NotImplementedError

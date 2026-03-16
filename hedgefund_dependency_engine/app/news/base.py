from __future__ import annotations

from abc import ABC, abstractmethod

from hedgefund_dependency_engine.app.models import NewsHeadline


class LiveNewsProvider(ABC):
    """Interface for fetching current macro-relevant headlines."""

    @abstractmethod
    def fetch_headlines(self, limit: int = 12) -> list[NewsHeadline]:
        raise NotImplementedError

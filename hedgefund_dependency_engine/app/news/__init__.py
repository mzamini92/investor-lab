"""Live news providers for dynamic scenario suggestions."""

from hedgefund_dependency_engine.app.news.base import LiveNewsProvider
from hedgefund_dependency_engine.app.news.rss_provider import GoogleNewsRSSProvider

__all__ = ["LiveNewsProvider", "GoogleNewsRSSProvider"]

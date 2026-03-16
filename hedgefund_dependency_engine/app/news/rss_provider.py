from __future__ import annotations

from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus
from xml.etree import ElementTree

import requests

from hedgefund_dependency_engine.app.exceptions import NewsProviderError
from hedgefund_dependency_engine.app.models import NewsHeadline
from hedgefund_dependency_engine.app.news.base import LiveNewsProvider


class GoogleNewsRSSProvider(LiveNewsProvider):
    """
    Lightweight live-news provider using public Google News RSS search feeds.

    This avoids paid APIs while remaining configurable enough for macro/event monitoring.
    """

    QUERY_GROUPS = {
        "macro": "markets OR economy OR inflation OR recession OR central bank",
        "geopolitics": "war OR sanctions OR shipping disruption OR missile OR oil shock",
        "health": "covid OR pandemic OR outbreak OR lockdown",
        "trade": "tariff OR trade war OR export controls OR customs",
        "technology": "AI capex OR semiconductors OR cloud spending OR data center",
    }

    def __init__(self, timeout_seconds: float = 8.0) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch_headlines(self, limit: int = 12) -> list[NewsHeadline]:
        if limit <= 0:
            return []

        headlines: list[NewsHeadline] = []
        seen_titles: set[str] = set()
        errors: list[str] = []

        per_group_limit = max(3, (limit // max(len(self.QUERY_GROUPS), 1)) + 1)
        for group_name, query in self.QUERY_GROUPS.items():
            url = (
                "https://news.google.com/rss/search?"
                f"q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
            )
            try:
                response = requests.get(url, timeout=self.timeout_seconds)
                response.raise_for_status()
                items = ElementTree.fromstring(response.content).findall(".//item")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{group_name}: {exc}")
                continue

            added_for_group = 0
            for item in items:
                title = (item.findtext("title") or "").strip()
                if not title or title in seen_titles:
                    continue
                link = (item.findtext("link") or "").strip()
                description = (item.findtext("description") or "").strip()
                pub_date = (item.findtext("pubDate") or "").strip()
                source = (item.findtext("source") or "Google News").strip()
                parsed_date = ""
                if pub_date:
                    try:
                        parsed_date = parsedate_to_datetime(pub_date).isoformat()
                    except Exception:  # noqa: BLE001
                        parsed_date = pub_date
                headline = NewsHeadline(
                    title=title,
                    source=source,
                    link=link,
                    published_at=parsed_date,
                    summary=description,
                    query_group=group_name,
                )
                headlines.append(headline)
                seen_titles.add(title)
                added_for_group += 1
                if added_for_group >= per_group_limit or len(headlines) >= limit:
                    break
            if len(headlines) >= limit:
                break

        if not headlines and errors:
            raise NewsProviderError("Unable to fetch live headlines from configured RSS sources.")
        return headlines[:limit]

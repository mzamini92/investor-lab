from __future__ import annotations

from typing import Any

from hedgefund_dependency_engine.app.models import EventTemplate, NewsHeadline


INTENSITY_KEYWORDS = {
    "severe": 0.35,
    "surge": 0.30,
    "crisis": 0.30,
    "escalate": 0.25,
    "attack": 0.25,
    "emergency": 0.25,
    "outbreak": 0.25,
    "lockdown": 0.25,
    "shortage": 0.20,
    "shock": 0.20,
    "spike": 0.20,
    "disruption": 0.20,
}


def headlines_to_context(headlines: list[NewsHeadline], limit: int = 8) -> str:
    return " ".join(headline.title for headline in headlines[:limit])


def suggest_dynamic_events_from_headlines(
    headlines: list[NewsHeadline],
    event_templates: list[EventTemplate],
    max_suggestions: int = 5,
) -> list[dict[str, Any]]:
    suggestions: list[dict[str, Any]] = []
    if not headlines or not event_templates:
        return suggestions

    for template in event_templates:
        matched_headlines: list[dict[str, Any]] = []
        total_keyword_hits = 0
        intensity_score = 0.0

        for headline in headlines:
            corpus = f"{headline.title} {headline.summary}".lower()
            matched_keywords = [keyword for keyword in template.trigger_keywords if keyword in corpus]
            if not matched_keywords:
                continue

            total_keyword_hits += len(matched_keywords)
            intensity_boost = 0.0
            for keyword, weight in INTENSITY_KEYWORDS.items():
                if keyword in corpus:
                    intensity_boost += weight
            intensity_score += intensity_boost
            matched_headlines.append(
                {
                    "title": headline.title,
                    "source": headline.source,
                    "link": headline.link,
                    "published_at": headline.published_at,
                    "matched_keywords": matched_keywords,
                }
            )

        if not matched_headlines:
            continue

        match_count = len(matched_headlines)
        base_confidence = min(1.0, (0.28 * match_count) + (0.08 * total_keyword_hits))
        confidence_score = min(100.0, (base_confidence + min(intensity_score, 0.35)) * 100.0)
        suggested_severity = min(2.0, max(0.5, template.default_severity + (0.15 * (match_count - 1)) + intensity_score))
        suggestions.append(
            {
                "event_name": template.name,
                "display_name": template.display_name,
                "description": template.description,
                "confidence_score": round(confidence_score, 2),
                "suggested_severity": round(suggested_severity, 2),
                "matched_headline_count": match_count,
                "matched_headlines": matched_headlines[:5],
                "rationale": f"{template.display_name} matched {match_count} current headlines across keywords {template.trigger_keywords}.",
            }
        )

    return sorted(
        suggestions,
        key=lambda item: (float(item["confidence_score"]), float(item["suggested_severity"])),
        reverse=True,
    )[:max_suggestions]

from __future__ import annotations

import re
from typing import Iterable


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def sentence_split(text: str) -> list[str]:
    normalized = normalize_text(text)
    if not normalized:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", normalized) if part.strip()]


def count_phrase_hits(text: str, phrases: Iterable[str]) -> dict[str, int]:
    lower_text = text.lower()
    result: dict[str, int] = {}
    for phrase in phrases:
        count = lower_text.count(phrase.lower())
        if count:
            result[phrase] = count
    return result


def first_sentences(text: str, limit: int = 2) -> str:
    return " ".join(sentence_split(text)[:limit]).strip()


def clip_text(text: str, limit: int = 220) -> str:
    normalized = normalize_text(text)
    return normalized if len(normalized) <= limit else normalized[: limit - 3].rstrip() + "..."

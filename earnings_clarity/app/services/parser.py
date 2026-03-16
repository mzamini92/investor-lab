from __future__ import annotations

import re
from typing import Iterable

from earnings_clarity.app.models import Transcript, TranscriptUtterance
from earnings_clarity.app.utils.constants import SECTION_MARKERS, SPEAKER_ROLE_KEYWORDS
from earnings_clarity.app.utils.text import normalize_text


SPEAKER_PATTERN = re.compile(r"^(?P<speaker>.+?)(?:\s+\((?P<role>[^)]+)\))?:\s*(?P<text>.+)$")


def _classify_role(speaker: str, role_hint: str | None) -> str:
    combined = f"{speaker} {role_hint or ''}".lower()
    for keyword, role in SPEAKER_ROLE_KEYWORDS.items():
        if keyword in combined:
            return role
    if any(firm in combined for firm in ("morgan", "goldman", "barclays", "ubs", "jpmorgan", "analyst")):
        return "analyst"
    return "unknown"


def _next_section(line: str, current_section: str) -> str:
    lowered = line.lower()
    for marker, section in SECTION_MARKERS.items():
        if marker in lowered:
            return section
    return current_section


def parse_raw_transcript(ticker: str, quarter: str, raw_text: str) -> Transcript:
    utterances: list[TranscriptUtterance] = []
    section = "operator"
    buffer_speaker: str | None = None
    buffer_role = "unknown"
    buffer_section = "operator"
    buffer_text: list[str] = []
    order = 0

    def flush() -> None:
        nonlocal order, buffer_speaker, buffer_role, buffer_section, buffer_text
        if buffer_speaker and buffer_text:
            utterances.append(
                TranscriptUtterance(
                    speaker=buffer_speaker,
                    speaker_role=buffer_role,  # type: ignore[arg-type]
                    section=buffer_section,  # type: ignore[arg-type]
                    text=normalize_text(" ".join(buffer_text)),
                    order=order,
                )
            )
            order += 1
        buffer_speaker = None
        buffer_role = "unknown"
        buffer_section = "unknown"
        buffer_text = []

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        section = _next_section(line, section)
        match = SPEAKER_PATTERN.match(line)
        if match:
            flush()
            buffer_speaker = match.group("speaker").strip()
            buffer_role = _classify_role(buffer_speaker, match.group("role"))
            if section == "operator" and buffer_role in {"ceo", "cfo", "executive", "unknown"}:
                buffer_section = "prepared_remarks"
            else:
                buffer_section = section
            buffer_text = [match.group("text").strip()]
        else:
            if buffer_speaker:
                buffer_text.append(line)
    flush()
    return Transcript(ticker=ticker, quarter=quarter, utterances=utterances, source="raw_text")


def transcript_to_text(utterances: Iterable[TranscriptUtterance]) -> str:
    return " ".join(utterance.text for utterance in utterances)

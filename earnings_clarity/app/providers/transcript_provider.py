from __future__ import annotations

import json
from pathlib import Path

from earnings_clarity.app.config import TRANSCRIPTS_DIR
from earnings_clarity.app.exceptions import TranscriptNotFoundError
from earnings_clarity.app.models import Transcript, TranscriptUtterance
from earnings_clarity.app.providers.base import TranscriptProvider
from earnings_clarity.app.services.parser import parse_raw_transcript


class LocalTranscriptProvider(TranscriptProvider):
    def __init__(self, transcripts_dir: Path = TRANSCRIPTS_DIR) -> None:
        self.transcripts_dir = Path(transcripts_dir)

    def get_transcript(self, ticker: str, quarter: str) -> Transcript:
        base_name = f"{ticker.upper()}_{quarter}"
        json_path = self.transcripts_dir / f"{base_name}.json"
        txt_path = self.transcripts_dir / f"{base_name}.txt"
        if json_path.exists():
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            utterances = [
                TranscriptUtterance(
                    speaker=item["speaker"],
                    speaker_role=item.get("speaker_role", "unknown"),
                    section=item.get("section", "unknown"),
                    text=item["text"],
                    order=int(item.get("order", index)),
                )
                for index, item in enumerate(payload["utterances"])
            ]
            return Transcript(ticker=ticker, quarter=quarter, utterances=utterances, source=str(json_path))
        if txt_path.exists():
            return parse_raw_transcript(ticker=ticker, quarter=quarter, raw_text=txt_path.read_text(encoding="utf-8"))
        raise TranscriptNotFoundError(f"Transcript not found for {ticker.upper()} {quarter}.")

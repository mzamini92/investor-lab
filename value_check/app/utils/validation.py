from __future__ import annotations


def validate_ticker(ticker: str) -> str:
    normalized = ticker.upper().strip()
    if not normalized:
        raise ValueError("Ticker cannot be empty.")
    return normalized

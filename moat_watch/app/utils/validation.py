from __future__ import annotations


def normalize_ticker(ticker: str) -> str:
    normalized = ticker.upper().strip()
    if not normalized:
        raise ValueError("Ticker cannot be empty.")
    return normalized


def normalize_quarter(quarter: str) -> str:
    normalized = quarter.upper().strip()
    if "Q" not in normalized:
        raise ValueError("Quarter must look like 2025Q2.")
    return normalized

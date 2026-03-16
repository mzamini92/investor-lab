from __future__ import annotations

from typing import Any

from earnings_clarity.app.exceptions import ValidationError
from earnings_clarity.app.models import HoldingPosition


def validate_holdings(payload: list[dict[str, Any]] | list[HoldingPosition]) -> list[HoldingPosition]:
    if not payload:
        raise ValidationError("Holdings cannot be empty.")
    holdings = [
        item if isinstance(item, HoldingPosition) else HoldingPosition(**item)
        for item in payload
    ]
    seen: set[str] = set()
    for holding in holdings:
        if holding.ticker in seen:
            raise ValidationError(f"Duplicate holding ticker: {holding.ticker}")
        seen.add(holding.ticker)
    return holdings

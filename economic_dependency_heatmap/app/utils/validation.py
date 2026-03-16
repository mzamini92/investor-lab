from __future__ import annotations

from typing import Any, Union

from economic_dependency_heatmap.app.exceptions import ValidationError
from economic_dependency_heatmap.app.models import PortfolioPosition


def validate_portfolio(payload: Union[list[dict[str, Any]], list[PortfolioPosition]]) -> list[PortfolioPosition]:
    if not payload:
        raise ValidationError("Portfolio cannot be empty.")

    positions = [item if isinstance(item, PortfolioPosition) else PortfolioPosition(**item) for item in payload]
    seen: set[str] = set()
    for position in positions:
        if position.ticker in seen:
            raise ValidationError(f"Duplicate ETF ticker: {position.ticker}")
        seen.add(position.ticker)
    return positions

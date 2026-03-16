from __future__ import annotations

from typing import Union

from economic_dependency_heatmap.app.models import PortfolioPosition


def normalize_portfolio_weights(positions: list[PortfolioPosition]) -> list[dict[str, Union[float, str]]]:
    total_amount = sum(position.amount for position in positions)
    return [
        {
            "ticker": position.ticker,
            "amount": round(position.amount, 2),
            "portfolio_weight": position.amount / total_amount,
        }
        for position in positions
    ]

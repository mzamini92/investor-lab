from __future__ import annotations

from itertools import combinations
from typing import Any

from hedgefund_dependency_engine.app.models import ETFHoldings


def _weight_map(holdings: ETFHoldings) -> dict[str, float]:
    return {holding.underlying_ticker: holding.holding_weight for holding in holdings.holdings}


def compute_pair_overlap(etf_a: str, etf_b: str, holdings_a: ETFHoldings, holdings_b: ETFHoldings, portfolio_weight_a: float, portfolio_weight_b: float) -> dict[str, Any]:
    weights_a = _weight_map(holdings_a)
    weights_b = _weight_map(holdings_b)
    tickers_a = set(weights_a)
    tickers_b = set(weights_b)
    intersection = tickers_a & tickers_b
    union = tickers_a | tickers_b
    shared_count = len(intersection)
    weighted_overlap = sum(min(weights_a[ticker], weights_b[ticker]) for ticker in intersection)
    max_weight_sum = sum(max(weights_a.get(ticker, 0.0), weights_b.get(ticker, 0.0)) for ticker in union)
    jaccard_overlap = weighted_overlap / max_weight_sum if max_weight_sum else 0.0
    practical_overlap = sum(min(portfolio_weight_a * weights_a[t], portfolio_weight_b * weights_b[t]) for t in intersection)
    return {
        "etf_a": etf_a,
        "etf_b": etf_b,
        "shared_holdings_count": shared_count,
        "union_holdings_count": len(union),
        "unweighted_overlap": shared_count / min(len(tickers_a), len(tickers_b)) if min(len(tickers_a), len(tickers_b)) else 0.0,
        "weighted_overlap": weighted_overlap,
        "jaccard_overlap": jaccard_overlap,
        "practical_overlap_contribution": practical_overlap,
    }


def build_overlap_matrix(holdings_map: dict[str, ETFHoldings], portfolio_weights: dict[str, float]) -> tuple[dict[str, dict[str, dict[str, Any]]], list[dict[str, Any]]]:
    tickers = sorted(holdings_map)
    matrix: dict[str, dict[str, dict[str, Any]]] = {ticker: {} for ticker in tickers}
    pairs: list[dict[str, Any]] = []
    for ticker in tickers:
        self_count = len(holdings_map[ticker].holdings)
        matrix[ticker][ticker] = {
            "etf_a": ticker,
            "etf_b": ticker,
            "shared_holdings_count": self_count,
            "union_holdings_count": self_count,
            "unweighted_overlap": 1.0,
            "weighted_overlap": 1.0,
            "jaccard_overlap": 1.0,
            "practical_overlap_contribution": portfolio_weights[ticker],
        }
    for etf_a, etf_b in combinations(tickers, 2):
        metrics = compute_pair_overlap(etf_a, etf_b, holdings_map[etf_a], holdings_map[etf_b], portfolio_weights[etf_a], portfolio_weights[etf_b])
        pairs.append(metrics)
        matrix[etf_a][etf_b] = metrics
        matrix[etf_b][etf_a] = {**metrics, "etf_a": etf_b, "etf_b": etf_a}
    return matrix, sorted(pairs, key=lambda row: float(row["weighted_overlap"]), reverse=True)

from __future__ import annotations

from collections.abc import Iterable
from typing import Union

import pandas as pd

from etf_overlap.config import MAGNIFICENT_7
from etf_overlap.models import ETFHoldings, PortfolioPosition


def normalize_portfolio(portfolio: Iterable[PortfolioPosition]) -> list[dict[str, Union[float, str]]]:
    positions = list(portfolio)
    total_amount = sum(position.amount for position in positions)
    return [
        {
            "ticker": position.ticker,
            "amount": round(position.amount, 2),
            "portfolio_weight": position.amount / total_amount,
        }
        for position in positions
    ]


def build_constituent_frame(
    portfolio: list[PortfolioPosition],
    holdings_map: dict[str, ETFHoldings],
) -> pd.DataFrame:
    total_amount = sum(position.amount for position in portfolio)
    rows: list[dict[str, object]] = []

    for position in portfolio:
        etf_weight = position.amount / total_amount
        etf_holdings = holdings_map[position.ticker]
        for holding in etf_holdings.holdings:
            rows.append(
                {
                    "fund_ticker": position.ticker,
                    "fund_amount": position.amount,
                    "fund_weight": etf_weight,
                    "stock_ticker": holding.stock_ticker,
                    "company_name": holding.company_name,
                    "holding_weight": holding.weight,
                    "exposure": etf_weight * holding.weight,
                    "sector": holding.sector or "Unknown",
                    "country": holding.country or "Unknown",
                    "market_cap": holding.market_cap,
                    "style_box": holding.style_box or "Unknown",
                }
            )
    return pd.DataFrame(rows)


def aggregate_underlying_exposures(constituent_frame: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        constituent_frame.groupby("stock_ticker", dropna=False)
        .agg(
            company_name=("company_name", "first"),
            exposure=("exposure", "sum"),
            sector=("sector", "first"),
            country=("country", "first"),
            market_cap=("market_cap", "max"),
            style_box=("style_box", "first"),
            contributing_etfs=("fund_ticker", lambda values: sorted(set(values))),
        )
        .reset_index()
    )
    grouped["contributing_etf_count"] = grouped["contributing_etfs"].apply(len)
    grouped = grouped.sort_values(["exposure", "stock_ticker"], ascending=[False, True]).reset_index(drop=True)
    grouped["exposure_pct"] = grouped["exposure"] * 100.0
    return grouped


def aggregate_dimension_exposure(constituent_frame: pd.DataFrame, dimension: str) -> pd.DataFrame:
    label = dimension if dimension in constituent_frame.columns else "Unknown"
    df = constituent_frame.copy()
    df[label] = df[label].fillna("Unknown")
    grouped = (
        df.groupby(label, dropna=False)
        .agg(exposure=("exposure", "sum"))
        .reset_index()
        .sort_values(["exposure", label], ascending=[False, True])
        .reset_index(drop=True)
    )
    grouped["exposure_pct"] = grouped["exposure"] * 100.0
    return grouped.rename(columns={label: "name"})


def compute_mag7_exposure(underlying_exposures: pd.DataFrame) -> dict[str, float]:
    exposure_map = dict(zip(underlying_exposures["stock_ticker"], underlying_exposures["exposure"]))
    result = {ticker: round(float(exposure_map.get(ticker, 0.0)), 6) for ticker in MAGNIFICENT_7}
    result["total"] = round(sum(result.values()), 6)
    return result

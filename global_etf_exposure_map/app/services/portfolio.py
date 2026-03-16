from __future__ import annotations

from collections import defaultdict
from typing import Any

import pandas as pd

from global_etf_exposure_map.app.models import ETFHoldings, PortfolioPosition
from global_etf_exposure_map.app.utils.normalization import normalize_portfolio_weights


def build_constituent_frame(
    positions: list[PortfolioPosition],
    holdings_map: dict[str, ETFHoldings],
) -> pd.DataFrame:
    normalized = normalize_portfolio_weights(positions)
    portfolio_weight_map = {row["ticker"]: float(row["portfolio_weight"]) for row in normalized}
    rows: list[dict[str, Any]] = []
    for position in positions:
        fund_weight = portfolio_weight_map[position.ticker]
        etf_holdings = holdings_map[position.ticker]
        for holding in etf_holdings.holdings:
            rows.append(
                {
                    "etf_ticker": position.ticker,
                    "label_region": etf_holdings.label_region,
                    "label_focus": etf_holdings.label_focus,
                    "fund_amount": position.amount,
                    "fund_weight": fund_weight,
                    "underlying_ticker": holding.underlying_ticker,
                    "company_name": holding.company_name,
                    "holding_weight": holding.holding_weight,
                    "exposure": fund_weight * holding.holding_weight,
                    "sector": holding.sector,
                    "country_domicile": holding.country_domicile,
                    "region": holding.region,
                    "currency": holding.currency,
                    "market_cap_bucket": holding.market_cap_bucket,
                    "country_code": holding.country_code,
                    "revenue_north_america": holding.revenue_north_america,
                    "revenue_europe": holding.revenue_europe,
                    "revenue_asia_pacific": holding.revenue_asia_pacific,
                    "revenue_emerging_markets": holding.revenue_emerging_markets,
                    "revenue_latin_america": holding.revenue_latin_america,
                    "revenue_middle_east_africa": holding.revenue_middle_east_africa,
                }
            )
    return pd.DataFrame(rows)


def compute_label_based_region_mix(normalized_portfolio: list[dict[str, Any]], holdings_map: dict[str, ETFHoldings]) -> dict[str, float]:
    region_mix: dict[str, float] = defaultdict(float)
    for row in normalized_portfolio:
        region_mix[holdings_map[row["ticker"]].label_region] += float(row["portfolio_weight"])
    return dict(region_mix)

from __future__ import annotations

from collections import defaultdict
from typing import Any

import pandas as pd

from economic_dependency_heatmap.app.models import ETFHoldings, PortfolioPosition
from economic_dependency_heatmap.app.utils.normalization import normalize_portfolio_weights


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
            row = {
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
                "profile_source": holding.profile_source,
                "revenue_us": holding.revenue_us,
                "revenue_europe": holding.revenue_europe,
                "revenue_china": holding.revenue_china,
                "revenue_apac_ex_china": holding.revenue_apac_ex_china,
                "revenue_japan": holding.revenue_japan,
                "revenue_latam": holding.revenue_latam,
                "revenue_mea": holding.revenue_mea,
                "revenue_other": holding.revenue_other,
                "us_consumer": holding.us_consumer,
                "china_demand": holding.china_demand,
                "europe_demand": holding.europe_demand,
                "ai_capex": holding.ai_capex,
                "cloud_spending": holding.cloud_spending,
                "global_semiconductors": holding.global_semiconductors,
                "energy_prices": holding.energy_prices,
                "industrial_capex": holding.industrial_capex,
                "emerging_market_growth": holding.emerging_market_growth,
                "healthcare_spending": holding.healthcare_spending,
                "financial_conditions": holding.financial_conditions,
                "usd_strength": holding.usd_strength,
                "interest_rate_sensitivity": holding.interest_rate_sensitivity,
            }
            rows.append(row)
    return pd.DataFrame(rows)


def compute_label_based_region_mix(
    normalized_portfolio: list[dict[str, Any]],
    holdings_map: dict[str, ETFHoldings],
) -> dict[str, float]:
    region_mix: dict[str, float] = defaultdict(float)
    for row in normalized_portfolio:
        region_mix[holdings_map[row["ticker"]].label_region] += float(row["portfolio_weight"])
    return dict(region_mix)

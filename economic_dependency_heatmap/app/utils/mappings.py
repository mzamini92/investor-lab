from __future__ import annotations

from typing import Any

from economic_dependency_heatmap.app.config import DEPENDENCY_COLUMNS, REVENUE_COLUMNS


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, float(value)))


def normalize_distribution(values: dict[str, float], fallback_key: str = "Other") -> dict[str, float]:
    cleaned = {key: max(float(value), 0.0) for key, value in values.items()}
    total = sum(cleaned.values())
    if total <= 0:
        return {key: 1.0 if key == fallback_key else 0.0 for key in cleaned}
    return {key: value / total for key, value in cleaned.items()}


def infer_revenue_profile(row: dict[str, Any]) -> dict[str, float]:
    country = str(row.get("country_domicile", "")).strip()
    region = str(row.get("region", "")).strip()
    sector = str(row.get("sector", "")).strip()
    revenue_na = float(row.get("revenue_north_america", 0.0) or 0.0)
    revenue_europe = float(row.get("revenue_europe", 0.0) or 0.0)
    revenue_apac = float(row.get("revenue_asia_pacific", 0.0) or 0.0)
    revenue_em = float(row.get("revenue_emerging_markets", 0.0) or 0.0)
    revenue_latam = float(row.get("revenue_latin_america", 0.0) or 0.0)
    revenue_mea = float(row.get("revenue_middle_east_africa", 0.0) or 0.0)

    if country == "United States":
        revenue_us = revenue_na * 0.85
    elif country == "Canada":
        revenue_us = revenue_na * 0.40
    else:
        revenue_us = revenue_na * 0.20

    if country == "China":
        revenue_china = max(revenue_em * 0.55, 0.40)
    elif sector in {"Technology", "Consumer Discretionary", "Materials", "Industrials"}:
        revenue_china = revenue_em * 0.35
    else:
        revenue_china = revenue_em * 0.20

    if country == "Japan":
        revenue_japan = max(revenue_apac * 0.55, 0.20)
    elif region == "Asia Pacific":
        revenue_japan = revenue_apac * 0.15
    else:
        revenue_japan = 0.02

    revenue_apac_ex_china = max(revenue_apac - revenue_japan, 0.0) * 0.85 + revenue_em * 0.10
    revenue_profile = normalize_distribution(
        {
            "United States": revenue_us,
            "Europe": revenue_europe,
            "China": revenue_china,
            "APAC ex-China": revenue_apac_ex_china,
            "Japan": revenue_japan,
            "Latin America": revenue_latam,
            "Middle East & Africa": revenue_mea,
            "Other": max(
                0.0,
                1.0
                - (
                    revenue_us
                    + revenue_europe
                    + revenue_china
                    + revenue_apac_ex_china
                    + revenue_japan
                    + revenue_latam
                    + revenue_mea
                ),
            ),
        }
    )
    return {column_name: revenue_profile[bucket] for bucket, column_name in REVENUE_COLUMNS.items()}


def infer_dependency_scores(row: dict[str, Any], revenue_profile: dict[str, float]) -> dict[str, float]:
    ticker = str(row.get("underlying_ticker", "")).upper().strip()
    sector = str(row.get("sector", "")).strip()
    region = str(row.get("region", "")).strip()
    currency = str(row.get("currency", "")).upper().strip()
    market_cap_bucket = str(row.get("market_cap_bucket", "")).strip()

    semis = {"NVDA", "TSM", "ASML", "AMD", "AVGO", "SAMSUNG ELECTRONICS CO. LTD."}
    cloud_names = {"MSFT", "AMZN", "GOOGL", "META", "ADBE", "SAP", "NFLX"}
    ai_names = {"NVDA", "MSFT", "AMZN", "GOOGL", "AVGO", "AMD", "TSM", "ASML", "META"}
    energy_names = {"XOM", "SHEL", "SAUDI ARAMCO", "VALE S.A.", "RIO"}
    financial_names = {"JPM", "HSBC", "COIN", "SQ", "BRK.B"}
    healthcare_names = {"LLY", "NVO", "MRK", "CRSP", "EXAS", "TDOC"}
    industrial_names = {"TSLA", "TM", "ASML", "SAP", "VALE S.A.", "RIO", "RELIANCE INDUSTRIES LTD."}

    scores = {name: 0.0 for name in DEPENDENCY_COLUMNS}
    scores["us_consumer"] = clamp(
        revenue_profile["revenue_us"]
        * (1.15 if sector in {"Consumer Discretionary", "Consumer Staples", "Communication Services"} else 0.75)
    )
    scores["china_demand"] = clamp(
        revenue_profile["revenue_china"]
        * (1.25 if sector in {"Technology", "Consumer Discretionary", "Materials", "Industrials"} else 1.0)
    )
    scores["europe_demand"] = clamp(
        revenue_profile["revenue_europe"]
        * (1.10 if sector in {"Industrials", "Healthcare", "Consumer Staples"} else 0.95)
    )
    scores["emerging_market_growth"] = clamp(
        revenue_profile["revenue_china"] * 0.50
        + revenue_profile["revenue_apac_ex_china"] * 0.45
        + revenue_profile["revenue_latam"] * 0.80
        + revenue_profile["revenue_mea"] * 0.70
    )
    scores["ai_capex"] = 0.78 if ticker in ai_names else (0.35 if sector == "Technology" and market_cap_bucket == "Mega Cap" else 0.08)
    scores["cloud_spending"] = 0.76 if ticker in cloud_names else (0.32 if sector in {"Technology", "Communication Services"} else 0.05)
    scores["global_semiconductors"] = 0.82 if ticker in semis else (0.18 if sector == "Technology" else 0.02)
    scores["energy_prices"] = 0.85 if ticker in energy_names else (0.25 if sector in {"Energy", "Materials", "Industrials"} else 0.03)
    scores["industrial_capex"] = 0.72 if ticker in industrial_names else (0.30 if sector in {"Industrials", "Materials", "Consumer Discretionary"} else 0.08)
    scores["healthcare_spending"] = 0.82 if ticker in healthcare_names else (0.18 if sector == "Healthcare" else 0.02)
    scores["financial_conditions"] = 0.82 if ticker in financial_names else (0.32 if sector == "Financials" else 0.08)
    scores["usd_strength"] = clamp((1.0 - revenue_profile["revenue_us"]) * 0.65 + (0.15 if currency != "USD" else 0.05))
    scores["interest_rate_sensitivity"] = clamp(
        0.72
        if ticker in financial_names or market_cap_bucket in {"Mid Cap", "Small Cap"}
        else (0.45 if sector in {"Technology", "Consumer Discretionary", "Real Estate"} else 0.18)
    )

    if region == "Emerging Markets":
        scores["emerging_market_growth"] = clamp(scores["emerging_market_growth"] + 0.20)
    if ticker in {"BABA", "TCEHY", "TSLA", "NVDA", "AAPL"}:
        scores["china_demand"] = clamp(scores["china_demand"] + 0.12)
    if ticker in {"XOM", "SHEL", "SAUDI ARAMCO"}:
        scores["usd_strength"] = clamp(scores["usd_strength"] + 0.10)
    return scores


def infer_profile_from_row(row: dict[str, Any]) -> dict[str, float]:
    revenue_profile = infer_revenue_profile(row)
    dependency_scores = infer_dependency_scores(row, revenue_profile)
    return {**revenue_profile, **dependency_scores, "profile_source": "inferred"}

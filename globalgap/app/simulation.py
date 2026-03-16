from __future__ import annotations

import pandas as pd

from globalgap.app.config import ASSET_RETURNS_FILE, DEFAULT_TREASURY_YIELD
from globalgap.app.models import (
    DiversificationAdjustment,
    PortfolioExposureSummary,
    SimulationPortfolioMetrics,
    SimulationSummary,
)


def load_asset_returns() -> pd.DataFrame:
    df = pd.read_csv(ASSET_RETURNS_FILE, parse_dates=["date"])
    return df.sort_values("date").reset_index(drop=True)


def suggest_diversification_adjustment(exposure: PortfolioExposureSummary) -> DiversificationAdjustment:
    current_intl = exposure.portfolio_international_weight
    if exposure.portfolio_us_weight >= 0.90:
        suggested_intl = 0.20
    elif exposure.portfolio_us_weight >= 0.80:
        suggested_intl = 0.15
    else:
        suggested_intl = max(current_intl, 0.10)

    suggested_intl = max(current_intl, suggested_intl)
    suggested_us = 1.0 - suggested_intl

    return DiversificationAdjustment(
        current_international_weight=round(current_intl, 4),
        suggested_international_weight=round(suggested_intl, 4),
        suggested_us_weight=round(suggested_us, 4),
        suggested_vehicle_examples=["VXUS", "VEA", "IEFA"],
        rationale="A modest international allocation can reduce home-country concentration and historically improved diversification when valuation and dollar conditions were more favorable abroad.",
    )


def _annualized_metrics(us_weight: float, intl_weight: float, returns_df: pd.DataFrame) -> SimulationPortfolioMetrics:
    monthly = returns_df[["us_equity_return", "international_equity_return"]]
    portfolio_series = (monthly["us_equity_return"] * us_weight) + (monthly["international_equity_return"] * intl_weight)
    mean_monthly = float(portfolio_series.mean())
    vol_monthly = float(portfolio_series.std(ddof=0))
    expected_return = mean_monthly * 12 * 100
    volatility = vol_monthly * (12 ** 0.5) * 100
    rf = DEFAULT_TREASURY_YIELD * 100
    sharpe = 0.0 if volatility == 0 else (expected_return - rf) / volatility
    return SimulationPortfolioMetrics(
        label="",
        us_weight=round(us_weight, 4),
        international_weight=round(intl_weight, 4),
        expected_annual_return_pct=round(expected_return, 2),
        annualized_volatility_pct=round(volatility, 2),
        sharpe_ratio=round(sharpe, 3),
    )


def run_diversification_simulation(exposure: PortfolioExposureSummary) -> tuple[SimulationSummary, DiversificationAdjustment, pd.DataFrame]:
    returns_df = load_asset_returns()
    adjustment = suggest_diversification_adjustment(exposure)

    current_metrics = _annualized_metrics(
        exposure.portfolio_us_weight,
        exposure.portfolio_international_weight,
        returns_df,
    )
    current_metrics.label = "Current Portfolio"

    diversified_metrics = _annualized_metrics(
        adjustment.suggested_us_weight,
        adjustment.suggested_international_weight,
        returns_df,
    )
    diversified_metrics.label = "Diversified Portfolio"

    sharpe_change = diversified_metrics.sharpe_ratio - current_metrics.sharpe_ratio
    expected_return_change = diversified_metrics.expected_annual_return_pct - current_metrics.expected_annual_return_pct
    volatility_change = diversified_metrics.annualized_volatility_pct - current_metrics.annualized_volatility_pct

    if sharpe_change >= 0:
        narrative = "The diversified mix improved historical risk-adjusted returns in the sample correlation set while reducing concentration in a single equity market."
    else:
        narrative = "The diversified mix reduced concentration risk, though the historical return trade-off was modest in the sample period."

    summary = SimulationSummary(
        current_portfolio=current_metrics,
        diversified_portfolio=diversified_metrics,
        sharpe_ratio_change=round(sharpe_change, 3),
        expected_return_change_pct=round(expected_return_change, 2),
        volatility_change_pct=round(volatility_change, 2),
        narrative=narrative,
    )
    return summary, adjustment, returns_df

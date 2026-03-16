from __future__ import annotations

from dataclasses import dataclass

from globalgap.app.models import HoldingExposure, PortfolioExposureSummary, PortfolioPosition


@dataclass(frozen=True)
class GeographyMapping:
    us_exposure_pct: float
    asset_class: str
    geography_label: str


GEOGRAPHY_MAP: dict[str, GeographyMapping] = {
    "VTI": GeographyMapping(0.99, "US Total Market ETF", "United States"),
    "VOO": GeographyMapping(1.00, "US Large Cap ETF", "United States"),
    "SPY": GeographyMapping(1.00, "US Large Cap ETF", "United States"),
    "QQQ": GeographyMapping(1.00, "US Growth ETF", "United States"),
    "VXUS": GeographyMapping(0.00, "International Equity ETF", "Global ex-US"),
    "VEA": GeographyMapping(0.00, "Developed Markets ETF", "Developed ex-US"),
    "IEFA": GeographyMapping(0.00, "Developed Markets ETF", "Developed ex-US"),
    "EFA": GeographyMapping(0.00, "Developed Markets ETF", "Developed ex-US"),
    "EWJ": GeographyMapping(0.00, "Single Country ETF", "Japan"),
    "EEM": GeographyMapping(0.02, "Emerging Markets ETF", "Emerging Markets"),
    "AAPL": GeographyMapping(1.00, "US Equity", "United States"),
    "MSFT": GeographyMapping(1.00, "US Equity", "United States"),
    "NVDA": GeographyMapping(1.00, "US Equity", "United States"),
    "AMZN": GeographyMapping(1.00, "US Equity", "United States"),
    "GOOGL": GeographyMapping(1.00, "US Equity", "United States"),
    "META": GeographyMapping(1.00, "US Equity", "United States"),
}


def _mapping_for_ticker(ticker: str) -> GeographyMapping:
    normalized = ticker.upper().strip()
    return GEOGRAPHY_MAP.get(normalized, GeographyMapping(1.00, "US Equity", "United States"))


def analyze_portfolio_exposure(positions: list[PortfolioPosition]) -> PortfolioExposureSummary:
    total_market_value = sum(position.quantity * position.price for position in positions)
    if total_market_value <= 0:
        raise ValueError("Portfolio market value must be positive.")

    holding_rows: list[HoldingExposure] = []
    us_weight = 0.0
    intl_weight = 0.0

    for position in positions:
        mapping = _mapping_for_ticker(position.ticker)
        market_value = position.quantity * position.price
        portfolio_weight = market_value / total_market_value
        holding_us_exposure = portfolio_weight * mapping.us_exposure_pct
        holding_intl_exposure = portfolio_weight * (1 - mapping.us_exposure_pct)
        us_weight += holding_us_exposure
        intl_weight += holding_intl_exposure

        holding_rows.append(
            HoldingExposure(
                ticker=position.ticker.upper(),
                market_value=round(market_value, 2),
                portfolio_weight=round(portfolio_weight, 6),
                us_exposure_pct=round(mapping.us_exposure_pct, 4),
                international_exposure_pct=round(1 - mapping.us_exposure_pct, 4),
                asset_class=mapping.asset_class,
                geography_label=mapping.geography_label,
            )
        )

    if us_weight >= 0.90:
        bias = "Severe US home bias"
    elif us_weight >= 0.80:
        bias = "High US home bias"
    elif us_weight >= 0.70:
        bias = "Moderate US home bias"
    else:
        bias = "More globally balanced"

    return PortfolioExposureSummary(
        total_market_value=round(total_market_value, 2),
        portfolio_us_weight=round(us_weight, 6),
        portfolio_international_weight=round(intl_weight, 6),
        home_bias_level=bias,
        holdings=holding_rows,
    )

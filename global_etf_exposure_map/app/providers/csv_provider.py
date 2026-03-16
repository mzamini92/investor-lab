from __future__ import annotations

from pathlib import Path

import pandas as pd

from global_etf_exposure_map.app.exceptions import HoldingsNotFoundError, ValidationError
from global_etf_exposure_map.app.models import ETFHoldings, HoldingRecord
from global_etf_exposure_map.app.providers.base import HoldingsProvider


class CSVHoldingsProvider(HoldingsProvider):
    ALIAS_MAP = {
        "SPY": "VOO",
        "IVV": "VOO",
        "SPLG": "VOO",
        "SCHX": "VOO",
        "ITOT": "VTI",
        "SCHB": "VTI",
        "VEU": "IXUS",
        "ACWX": "IXUS",
        "IEMG": "EEM",
        "VWO": "EEM",
        "ONEQ": "QQQ",
        "QQQM": "QQQ",
        "VEA": "IXUS",
        "IEFA": "IXUS",
        "EFA": "IXUS",
        "SCHF": "IXUS",
    }
    REQUIRED_COLUMNS = {
        "etf_ticker",
        "underlying_ticker",
        "company_name",
        "holding_weight",
        "sector",
        "country_domicile",
        "region",
        "currency",
        "market_cap_bucket",
        "country_code",
        "label_region",
        "label_focus",
    }

    def __init__(self, holdings_dir: Path) -> None:
        self.holdings_dir = Path(holdings_dir)
        if not self.holdings_dir.exists():
            raise ValidationError(f"Holdings directory does not exist: {self.holdings_dir}")

    def get_holdings(self, ticker: str) -> ETFHoldings:
        normalized_ticker = ticker.upper().strip()
        canonical_ticker = self.ALIAS_MAP.get(normalized_ticker, normalized_ticker)
        path = self.holdings_dir / f"{canonical_ticker}.csv"
        if not path.exists():
            raise HoldingsNotFoundError(f"Holdings CSV not found for ETF {normalized_ticker}: {path}")

        df = pd.read_csv(path)
        missing_columns = self.REQUIRED_COLUMNS - set(df.columns)
        if missing_columns:
            raise ValidationError(f"Missing columns in {path}: {sorted(missing_columns)}")

        label_region = str(df["label_region"].iloc[0])
        label_focus = str(df["label_focus"].iloc[0])
        holdings = [
            HoldingRecord(
                etf_ticker=str(row["etf_ticker"]),
                underlying_ticker=str(row["underlying_ticker"]),
                company_name=str(row["company_name"]),
                holding_weight=float(row["holding_weight"]),
                sector=str(row["sector"]),
                country_domicile=str(row["country_domicile"]),
                region=str(row["region"]),
                currency=str(row["currency"]),
                market_cap_bucket=str(row["market_cap_bucket"]),
                revenue_north_america=float(row.get("revenue_north_america", 0.0)),
                revenue_europe=float(row.get("revenue_europe", 0.0)),
                revenue_asia_pacific=float(row.get("revenue_asia_pacific", 0.0)),
                revenue_emerging_markets=float(row.get("revenue_emerging_markets", 0.0)),
                revenue_latin_america=float(row.get("revenue_latin_america", 0.0)),
                revenue_middle_east_africa=float(row.get("revenue_middle_east_africa", 0.0)),
                country_code=str(row["country_code"]),
            )
            for _, row in df.iterrows()
        ]
        return ETFHoldings(
            ticker=normalized_ticker,
            label_region=label_region,
            label_focus=label_focus,
            holdings=holdings,
        ).normalized()

    def supported_etfs(self) -> list[str]:
        supported = {path.stem.upper() for path in self.holdings_dir.glob("*.csv")}
        for alias, canonical in self.ALIAS_MAP.items():
            if canonical in supported:
                supported.add(alias)
        return sorted(supported)

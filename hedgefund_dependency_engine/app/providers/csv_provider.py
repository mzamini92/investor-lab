from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

from hedgefund_dependency_engine.app.config import COMPANY_PROFILES_PATH, DEPENDENCY_COLUMNS, EVENT_TEMPLATES_PATH, SCENARIOS_PATH
from hedgefund_dependency_engine.app.exceptions import HoldingsNotFoundError, ValidationError
from hedgefund_dependency_engine.app.models import CompanyProfile, ETFHoldings, EventTemplate, HoldingRecord, MacroScenario
from hedgefund_dependency_engine.app.providers.base import EngineDataProvider
from hedgefund_dependency_engine.app.utils.mappings import infer_profile_from_row


class CSVEngineDataProvider(EngineDataProvider):
    ALIAS_MAP = {
        "SPY": "VOO",
        "IVV": "VOO",
        "SPLG": "VOO",
        "SCHX": "VOO",
        "ITOT": "VTI",
        "SCHB": "VTI",
        "VEU": "IXUS",
        "ACWX": "IXUS",
        "VEA": "IXUS",
        "IEFA": "IXUS",
        "EFA": "IXUS",
        "SCHF": "IXUS",
        "IEMG": "EEM",
        "VWO": "EEM",
        "ONEQ": "QQQ",
        "QQQM": "QQQ",
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

    def __init__(
        self,
        holdings_dir: Path,
        company_profiles_path: Path = COMPANY_PROFILES_PATH,
        scenarios_path: Path = SCENARIOS_PATH,
        event_templates_path: Path = EVENT_TEMPLATES_PATH,
    ) -> None:
        self.holdings_dir = Path(holdings_dir)
        self.company_profiles_path = Path(company_profiles_path)
        self.scenarios_path = Path(scenarios_path)
        self.event_templates_path = Path(event_templates_path)
        if not self.holdings_dir.exists():
            raise ValidationError(f"Holdings directory does not exist: {self.holdings_dir}")
        self._company_profiles = self._load_company_profiles()
        self._scenarios = self._load_scenarios()
        self._event_templates = self._load_event_templates()

    def get_holdings(self, ticker: str) -> ETFHoldings:
        normalized_ticker = ticker.upper().strip()
        canonical_ticker = self.ALIAS_MAP.get(normalized_ticker, normalized_ticker)
        path = self.holdings_dir / f"{canonical_ticker}.csv"
        if not path.exists():
            raise HoldingsNotFoundError(f"Holdings CSV not found for ETF {normalized_ticker}: {path}")
        df = pd.read_csv(path)
        missing = self.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValidationError(f"Missing columns in {path}: {sorted(missing)}")
        label_region = str(df["label_region"].iloc[0])
        label_focus = str(df["label_focus"].iloc[0])
        holdings: list[HoldingRecord] = []
        for _, row in df.iterrows():
            raw = row.to_dict()
            ticker_symbol = str(raw["underlying_ticker"]).upper().strip()
            profile = self._company_profiles.get(ticker_symbol)
            profile_dict = self._profile_to_dict(profile) if profile is not None else infer_profile_from_row(raw)
            holdings.append(
                HoldingRecord(
                    etf_ticker=str(raw["etf_ticker"]),
                    underlying_ticker=ticker_symbol,
                    company_name=str(raw["company_name"]),
                    holding_weight=float(raw["holding_weight"]),
                    sector=str(raw["sector"]),
                    country_domicile=str(raw["country_domicile"]),
                    region=str(raw["region"]),
                    currency=str(raw["currency"]),
                    market_cap_bucket=str(raw["market_cap_bucket"]),
                    country_code=str(raw["country_code"]),
                    revenue_us=float(profile_dict["revenue_us"]),
                    revenue_europe=float(profile_dict["revenue_europe"]),
                    revenue_china=float(profile_dict["revenue_china"]),
                    revenue_apac_ex_china=float(profile_dict["revenue_apac_ex_china"]),
                    revenue_japan=float(profile_dict["revenue_japan"]),
                    revenue_latam=float(profile_dict["revenue_latam"]),
                    revenue_mea=float(profile_dict["revenue_mea"]),
                    revenue_other=float(profile_dict["revenue_other"]),
                    us_consumer=float(profile_dict["us_consumer"]),
                    china_demand=float(profile_dict["china_demand"]),
                    europe_demand=float(profile_dict["europe_demand"]),
                    ai_capex=float(profile_dict["ai_capex"]),
                    cloud_spending=float(profile_dict["cloud_spending"]),
                    global_semiconductors=float(profile_dict["global_semiconductors"]),
                    industrial_capex=float(profile_dict["industrial_capex"]),
                    energy_prices=float(profile_dict["energy_prices"]),
                    healthcare_spending=float(profile_dict["healthcare_spending"]),
                    financial_conditions=float(profile_dict["financial_conditions"]),
                    usd_strength=float(profile_dict["usd_strength"]),
                    interest_rate_sensitivity=float(profile_dict["interest_rate_sensitivity"]),
                    emerging_market_growth=float(profile_dict["emerging_market_growth"]),
                    profile_source=str(profile_dict["profile_source"]),
                )
            )
        return ETFHoldings(ticker=normalized_ticker, label_region=label_region, label_focus=label_focus, holdings=holdings).normalized()

    def get_scenarios(self) -> list[MacroScenario]:
        return list(self._scenarios)

    def get_event_templates(self) -> list[EventTemplate]:
        return list(self._event_templates)

    def supported_etfs(self) -> list[str]:
        supported = {path.stem.upper() for path in self.holdings_dir.glob("*.csv")}
        for alias, canonical in self.ALIAS_MAP.items():
            if canonical in supported:
                supported.add(alias)
        return sorted(supported)

    def _load_company_profiles(self) -> dict[str, CompanyProfile]:
        if not self.company_profiles_path.exists():
            return {}
        df = pd.read_csv(self.company_profiles_path).fillna(0.0)
        result: dict[str, CompanyProfile] = {}
        for _, row in df.iterrows():
            raw = row.to_dict()
            raw["underlying_ticker"] = str(raw["underlying_ticker"]).upper().strip()
            raw["profile_source"] = str(raw.get("profile_source", "curated"))
            result[raw["underlying_ticker"]] = CompanyProfile(**raw)
        return result

    def _load_scenarios(self) -> list[MacroScenario]:
        if not self.scenarios_path.exists():
            return []
        df = pd.read_csv(self.scenarios_path).fillna(0.0)
        scenarios: list[MacroScenario] = []
        for _, row in df.iterrows():
            raw = row.to_dict()
            shock_weights = {dependency_name: float(raw.get(dependency_name, 0.0)) for dependency_name in DEPENDENCY_COLUMNS}
            scenarios.append(
                MacroScenario(
                    name=str(raw["name"]),
                    display_name=str(raw["display_name"]),
                    description=str(raw["description"]),
                    shock_weights=shock_weights,
                )
            )
        return scenarios

    def _load_event_templates(self) -> list[EventTemplate]:
        if not self.event_templates_path.exists():
            return []
        df = pd.read_csv(self.event_templates_path).fillna("")
        templates: list[EventTemplate] = []
        for _, row in df.iterrows():
            raw = row.to_dict()
            shock_weights = {dependency_name: float(raw.get(dependency_name, 0.0) or 0.0) for dependency_name in DEPENDENCY_COLUMNS}
            templates.append(
                EventTemplate(
                    name=str(raw["name"]),
                    display_name=str(raw["display_name"]),
                    description=str(raw["description"]),
                    trigger_keywords=[
                        keyword
                        for keyword in str(raw.get("trigger_keywords", "")).split("|")
                        if keyword.strip()
                    ],
                    default_severity=float(raw.get("default_severity", 1.0) or 1.0),
                    shock_weights=shock_weights,
                )
            )
        return templates

    @staticmethod
    def _profile_to_dict(profile: CompanyProfile) -> dict[str, Union[float, str]]:
        return {
            "revenue_us": profile.revenue_us,
            "revenue_europe": profile.revenue_europe,
            "revenue_china": profile.revenue_china,
            "revenue_apac_ex_china": profile.revenue_apac_ex_china,
            "revenue_japan": profile.revenue_japan,
            "revenue_latam": profile.revenue_latam,
            "revenue_mea": profile.revenue_mea,
            "revenue_other": profile.revenue_other,
            "us_consumer": profile.us_consumer,
            "china_demand": profile.china_demand,
            "europe_demand": profile.europe_demand,
            "ai_capex": profile.ai_capex,
            "cloud_spending": profile.cloud_spending,
            "global_semiconductors": profile.global_semiconductors,
            "industrial_capex": profile.industrial_capex,
            "energy_prices": profile.energy_prices,
            "healthcare_spending": profile.healthcare_spending,
            "financial_conditions": profile.financial_conditions,
            "usd_strength": profile.usd_strength,
            "interest_rate_sensitivity": profile.interest_rate_sensitivity,
            "emerging_market_growth": profile.emerging_market_growth,
            "profile_source": profile.profile_source,
        }

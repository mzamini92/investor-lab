from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent
DATA_ROOT = APP_ROOT / "data"
ETF_HOLDINGS_DIR = DATA_ROOT / "etf_holdings"
METADATA_DIR = DATA_ROOT / "metadata"
SCENARIOS_DIR = DATA_ROOT / "scenarios"
COMPANY_PROFILES_PATH = METADATA_DIR / "company_profiles.csv"
SCENARIOS_PATH = SCENARIOS_DIR / "sample_scenarios.csv"
EVENT_TEMPLATES_PATH = SCENARIOS_DIR / "event_templates.csv"

DEFAULT_SAMPLE_PORTFOLIO = [
    {"ticker": "VTI", "amount": 2000.0},
    {"ticker": "QQQ", "amount": 1000.0},
    {"ticker": "VXUS", "amount": 1500.0},
    {"ticker": "EEM", "amount": 500.0},
    {"ticker": "ARKK", "amount": 300.0},
]

REVENUE_COLUMNS = {
    "United States": "revenue_us",
    "Europe": "revenue_europe",
    "China": "revenue_china",
    "APAC ex-China": "revenue_apac_ex_china",
    "Japan": "revenue_japan",
    "Latin America": "revenue_latam",
    "Middle East & Africa": "revenue_mea",
    "Other": "revenue_other",
}

DEPENDENCY_COLUMNS = {
    "us_consumer": {"display_name": "US Economy / Consumer", "category_group": "Demand Centers"},
    "china_demand": {"display_name": "China Demand", "category_group": "Demand Centers"},
    "europe_demand": {"display_name": "Europe Demand", "category_group": "Demand Centers"},
    "ai_capex": {"display_name": "AI Capex", "category_group": "Technology Engines"},
    "cloud_spending": {"display_name": "Cloud Spending", "category_group": "Technology Engines"},
    "global_semiconductors": {"display_name": "Global Semiconductors", "category_group": "Technology Engines"},
    "industrial_capex": {"display_name": "Industrial Capex", "category_group": "Macro Cycles"},
    "energy_prices": {"display_name": "Energy Prices", "category_group": "Macro Cycles"},
    "healthcare_spending": {"display_name": "Healthcare Spending", "category_group": "Structural Demand"},
    "financial_conditions": {"display_name": "Financial Conditions", "category_group": "Rates & Liquidity"},
    "usd_strength": {"display_name": "USD Strength", "category_group": "Rates & Liquidity"},
    "interest_rate_sensitivity": {"display_name": "Interest-Rate Sensitivity", "category_group": "Rates & Liquidity"},
    "emerging_market_growth": {"display_name": "Emerging Market Growth", "category_group": "Demand Centers"},
}

DEFAULT_SCENARIO_NAMES = (
    "china_slowdown",
    "europe_recession",
    "ai_boom",
    "usd_surge",
    "energy_spike",
    "fed_tightening",
    "em_rebound",
)

DEFAULT_DYNAMIC_EVENTS = (
    "war_supply_shock",
    "pandemic_wave",
    "tariff_escalation",
)

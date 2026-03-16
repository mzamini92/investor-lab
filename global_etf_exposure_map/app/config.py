from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent
DATA_ROOT = APP_ROOT / "data"
ETF_HOLDINGS_DIR = DATA_ROOT / "etf_holdings"
METADATA_DIR = DATA_ROOT / "metadata"

DEFAULT_SAMPLE_PORTFOLIO = [
    {"ticker": "VTI", "amount": 1750.0},
    {"ticker": "VOO", "amount": 1250.0},
    {"ticker": "QQQ", "amount": 900.0},
    {"ticker": "ARKK", "amount": 350.0},
    {"ticker": "VXUS", "amount": 1250.0},
    {"ticker": "EEM", "amount": 500.0},
    {"ticker": "IXUS", "amount": 900.0},
    {"ticker": "SCHD", "amount": 700.0},
]

DEFAULT_REVENUE_REGIONS = (
    "North America",
    "Europe",
    "Asia Pacific",
    "Emerging Markets",
    "Latin America",
    "Middle East & Africa",
)

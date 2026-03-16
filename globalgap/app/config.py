from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PACKAGE_ROOT / "data"

VALUATION_HISTORY_FILE = DATA_ROOT / "valuation_history.csv"
EARNINGS_GROWTH_FILE = DATA_ROOT / "earnings_growth.csv"
DOLLAR_HISTORY_FILE = DATA_ROOT / "dollar_history.csv"
ASSET_RETURNS_FILE = DATA_ROOT / "asset_returns.csv"
SAMPLE_PORTFOLIO_FILE = PACKAGE_ROOT / "sample_portfolio.json"

DEFAULT_TREASURY_YIELD = 0.042
DEFAULT_ANALOG_COUNT = 3

from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent
DATA_ROOT = APP_ROOT / "data"
SAMPLES_DIR = DATA_ROOT / "samples"
HISTORICAL_DIR = DATA_ROOT / "historical"

DEFAULT_CURRENT_SNAPSHOT_FILE = SAMPLES_DIR / "current_snapshot.json"
DEFAULT_PRIOR_SNAPSHOT_FILE = SAMPLES_DIR / "prior_snapshot.json"
DEFAULT_HISTORY_FILE = HISTORICAL_DIR / "historical_macro.csv"

DEFAULT_ANALOG_FIELDS = [
    "fed_funds_rate",
    "cpi_yoy",
    "inflation_3m_annualized",
    "unemployment_rate",
    "unemployment_3m_change",
    "ism_manufacturing",
    "term_spread_2s10s",
    "high_yield_spread",
    "earnings_revision_breadth",
]

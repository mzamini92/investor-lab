from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent
DATA_ROOT = APP_ROOT / "data"
CURRENT_DIR = DATA_ROOT / "current"
HISTORICAL_DIR = DATA_ROOT / "historical"
PEERS_DIR = DATA_ROOT / "peers"
RATES_DIR = DATA_ROOT / "rates"

CURRENT_SNAPSHOT_FILE = CURRENT_DIR / "valuation_snapshots.json"
HISTORICAL_FILE = HISTORICAL_DIR / "valuation_history.csv"
PEER_GROUP_FILE = PEERS_DIR / "peer_groups.json"
TREASURY_RATE_FILE = RATES_DIR / "treasury_yields.json"

DEFAULT_LOOKBACK_YEARS = 10
DEFAULT_SAMPLE_TICKERS = ["AAPL", "MSFT", "NVDA", "VOO", "QQQ", "SNOW"]

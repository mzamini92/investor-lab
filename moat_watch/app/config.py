from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent
DATA_ROOT = APP_ROOT / "data"
COMPANIES_FILE = DATA_ROOT / "companies" / "quarterly_metrics.csv"
PEER_GROUPS_FILE = DATA_ROOT / "peers" / "peer_groups.json"
COMMENTARY_FILE = DATA_ROOT / "commentary" / "quarterly_commentary.json"
WATCHLIST_FILE = DATA_ROOT / "watchlists" / "sample_watchlist.json"

DEFAULT_QUARTER = "2025Q2"
DEFAULT_WATCHLIST = [
    {"ticker": "SBUX"},
    {"ticker": "AAPL"},
    {"ticker": "MSFT"},
    {"ticker": "NFLX"},
    {"ticker": "COST"},
]

from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent
DATA_ROOT = APP_ROOT / "data"
TRANSCRIPTS_DIR = DATA_ROOT / "transcripts"
EARNINGS_DIR = DATA_ROOT / "earnings"
HOLDINGS_DIR = DATA_ROOT / "holdings"

DEFAULT_SAMPLE_HOLDINGS = [
    {"ticker": "AAPL", "shares": 10.0},
    {"ticker": "MSFT", "shares": 6.0},
    {"ticker": "NVDA", "shares": 3.0},
]

DEFAULT_SAMPLE_QUARTER = "2025Q4"

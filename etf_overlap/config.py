from pathlib import Path

MAGNIFICENT_7 = ("AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA")

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "holdings"

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

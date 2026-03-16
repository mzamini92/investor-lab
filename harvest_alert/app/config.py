from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent
DATA_ROOT = APP_ROOT / "data"
ACCOUNTS_FILE = DATA_ROOT / "accounts" / "accounts.json"
POSITIONS_FILE = DATA_ROOT / "positions" / "positions.json"
LOTS_FILE = DATA_ROOT / "positions" / "lots.json"
TRANSACTIONS_FILE = DATA_ROOT / "transactions" / "transactions.json"
REPLACEMENTS_FILE = DATA_ROOT / "replacements" / "replacements.json"
TAX_ASSUMPTIONS_FILE = DATA_ROOT / "sample" / "tax_assumptions.json"

DEFAULT_SCAN_DATE = "2026-03-15"

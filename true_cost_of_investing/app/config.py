from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent
DATA_ROOT = APP_ROOT / "data"
PORTFOLIOS_DIR = DATA_ROOT / "portfolios"
ASSUMPTIONS_DIR = DATA_ROOT / "assumptions"
SAMPLES_DIR = DATA_ROOT / "samples"

DEFAULT_PORTFOLIO_FILE = PORTFOLIOS_DIR / "sample_high_fee_portfolio.json"
DEFAULT_ALTERNATIVE_PORTFOLIO_FILE = PORTFOLIOS_DIR / "sample_low_cost_portfolio.json"
DEFAULT_ASSUMPTIONS_FILE = ASSUMPTIONS_DIR / "taxable_account.json"

DEFAULT_ASSUMED_REALIZED_GAIN_RATIO = 0.30
DEFAULT_REBALANCE_TRADE_FRACTION = 0.10
DEFAULT_SHORT_TERM_CASH_RETURN = 0.02
DEFAULT_CONFIDENCE_MESSAGE = (
    "This tool estimates long-term investing friction using transparent assumptions. "
    "It is designed for education and portfolio-cost awareness, not tax filing or personalized advice."
)

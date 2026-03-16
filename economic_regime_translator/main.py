from pathlib import Path
import sys


CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from economic_regime_translator.app.cli import main


if __name__ == "__main__":
    raise SystemExit(main())

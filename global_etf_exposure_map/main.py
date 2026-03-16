from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from global_etf_exposure_map.app.cli import main


if __name__ == "__main__":
    raise SystemExit(main())

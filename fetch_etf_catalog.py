from __future__ import annotations

import argparse
from pathlib import Path

from etf_catalog.fetcher import save_etf_catalog


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch a U.S.-listed ETF catalog from Nasdaq Trader.")
    parser.add_argument(
        "--output",
        default="data/catalog/us_etf_catalog.csv",
        help="Output path for the ETF catalog CSV.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    output_path = save_etf_catalog(Path(args.output))
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


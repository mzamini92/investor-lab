from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from etf_ingest.ingestor import import_holdings_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bulk import ETF holdings into the local analytics datasets.")
    parser.add_argument("--source-csv", required=True, help="Path to a standardized raw holdings CSV.")
    parser.add_argument(
        "--target",
        choices=("both", "overlap", "global"),
        default="both",
        help="Which dataset(s) to generate.",
    )
    parser.add_argument("--metadata-csv", help="Optional country/region metadata CSV override.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing ETF files if present.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON summary.")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    summaries = import_holdings_csv(
        source_csv=Path(args.source_csv),
        metadata_csv=Path(args.metadata_csv) if args.metadata_csv else None,
        target=args.target,
        overwrite=args.overwrite,
    )
    output = [summary.__dict__ for summary in summaries]
    print(json.dumps(output, indent=2 if args.pretty else None))
    return 0


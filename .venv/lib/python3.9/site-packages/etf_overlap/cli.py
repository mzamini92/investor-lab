from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional, Union

from etf_overlap.config import DEFAULT_DATA_DIR
from etf_overlap.engine import PortfolioAnalyzer
from etf_overlap.providers.csv_provider import CSVHoldingsProvider


def _load_portfolio(path: Union[str, Path]) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict) and "positions" in payload:
        return payload["positions"]
    if not isinstance(payload, list):
        raise ValueError("Portfolio JSON must be a list of positions or an object with a 'positions' key.")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze ETF portfolio overlap and hidden concentration.")
    parser.add_argument("--portfolio", required=True, help="Path to a portfolio JSON file.")
    parser.add_argument(
        "--data-dir",
        default=str(DEFAULT_DATA_DIR),
        help="Directory containing ETF holdings CSV files.",
    )
    parser.add_argument("--output", help="Optional path to write the analysis JSON.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    provider = CSVHoldingsProvider(args.data_dir)
    analyzer = PortfolioAnalyzer(provider)
    portfolio = _load_portfolio(args.portfolio)
    result = analyzer.analyze(portfolio).to_dict()

    indent = 2 if args.pretty else None
    output_text = json.dumps(result, indent=indent)
    if args.output:
        Path(args.output).write_text(output_text + ("\n" if indent else ""), encoding="utf-8")
    else:
        print(output_text)
    return 0

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from true_cost_of_investing.app.config import (
    DEFAULT_ALTERNATIVE_PORTFOLIO_FILE,
    DEFAULT_ASSUMPTIONS_FILE,
    DEFAULT_PORTFOLIO_FILE,
)
from true_cost_of_investing.app.providers.assumptions_provider import AssumptionsProvider
from true_cost_of_investing.app.providers.portfolio_provider import PortfolioProvider
from true_cost_of_investing.app.services.analyzer import TrueCostAnalyzer
from true_cost_of_investing.app.services.reporting import build_markdown_report
from true_cost_of_investing.app.services.visualization import save_charts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="True Cost of Investing Calculator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze a single portfolio.")
    analyze.add_argument("--portfolio", default=str(DEFAULT_PORTFOLIO_FILE))
    analyze.add_argument("--assumptions", default=str(DEFAULT_ASSUMPTIONS_FILE))
    analyze.add_argument("--output-json")
    analyze.add_argument("--output-md")
    analyze.add_argument("--output-dir", default="./output")
    analyze.add_argument("--save-charts", action="store_true")
    analyze.add_argument("--pretty", action="store_true")

    compare = subparsers.add_parser("compare", help="Compare current vs alternative portfolios.")
    compare.add_argument("--current", default=str(DEFAULT_PORTFOLIO_FILE))
    compare.add_argument("--alternative", default=str(DEFAULT_ALTERNATIVE_PORTFOLIO_FILE))
    compare.add_argument("--assumptions", default=str(DEFAULT_ASSUMPTIONS_FILE))
    compare.add_argument("--output-json")
    compare.add_argument("--output-md")
    compare.add_argument("--output-dir", default="./output")
    compare.add_argument("--save-charts", action="store_true")
    compare.add_argument("--pretty", action="store_true")

    return parser


def _write_optional(path: Optional[str], contents: str) -> None:
    if not path:
        return
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(contents, encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    portfolio_provider = PortfolioProvider()
    assumptions_provider = AssumptionsProvider()
    analyzer = TrueCostAnalyzer()

    if args.command == "analyze":
        holdings = portfolio_provider.load(Path(args.portfolio))
        assumptions = assumptions_provider.load(Path(args.assumptions))
        result = analyzer.analyze(holdings, assumptions).to_dict()
        if args.save_charts:
            result["saved_charts"] = save_charts(result, args.output_dir)
        payload = json.dumps(result, indent=2 if args.pretty else None)
        _write_optional(args.output_json, payload + ("\n" if args.pretty else ""))
        _write_optional(args.output_md, build_markdown_report(result))
        if not args.output_json:
            print(payload)
        return 0

    current = portfolio_provider.load(Path(args.current))
    alternative = portfolio_provider.load(Path(args.alternative))
    assumptions = assumptions_provider.load(Path(args.assumptions))
    result = analyzer.compare(current, alternative, assumptions).to_dict()
    if args.save_charts:
        result["saved_charts"] = save_charts(result["current"], args.output_dir)
    payload = json.dumps(result, indent=2 if args.pretty else None)
    _write_optional(args.output_json, payload + ("\n" if args.pretty else ""))
    _write_optional(args.output_md, build_markdown_report(result["current"]))
    if not args.output_json:
        print(payload)
    return 0

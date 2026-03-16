from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from value_check.app.services.analyzer import ValueCheckAnalyzer
from value_check.app.services.reporting import build_markdown_report
from value_check.app.services.visualization import plot_peer_comparison, plot_percentile_bars, plot_scorecard


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ValueCheck")
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check")
    check.add_argument("--ticker", required=True)
    check.add_argument("--lookback", type=int, default=10)
    check.add_argument("--treasury-yield", type=float)
    check.add_argument("--asset-type", default="auto")
    check.add_argument("--peer-group")
    check.add_argument("--output-json")
    check.add_argument("--output-md")
    check.add_argument("--output-dir", default="./output")
    check.add_argument("--save-charts", action="store_true")
    check.add_argument("--pretty", action="store_true")
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
    analyzer = ValueCheckAnalyzer()
    result = analyzer.analyze(
        args.ticker,
        lookback_years=args.lookback,
        treasury_yield=args.treasury_yield,
        peer_group=args.peer_group,
    ).to_dict()

    if args.save_charts:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        plot_percentile_bars(result["historical_comparison"]).write_html(str(output_dir / "history.html"))
        plot_peer_comparison(result["peer_comparison"]).write_html(str(output_dir / "peers.html"))
        plot_scorecard(result).write_html(str(output_dir / "scorecard.html"))

    payload = json.dumps(result, indent=2 if args.pretty else None)
    _write_optional(args.output_json, payload + ("\n" if args.pretty else ""))
    _write_optional(args.output_md, build_markdown_report(result))
    if not args.output_json:
        print(payload)
    return 0

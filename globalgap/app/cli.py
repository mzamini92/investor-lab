from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, Union

from globalgap.app.analyzer import GlobalGapAnalyzer
from globalgap.app.config import SAMPLE_PORTFOLIO_FILE
from globalgap.app.models import PortfolioPosition
from globalgap.app.visualization import save_chart_bundle


def _load_positions(path: Optional[Union[str, Path]]) -> list[PortfolioPosition]:
    target = Path(path) if path else SAMPLE_PORTFOLIO_FILE
    payload = json.loads(target.read_text(encoding="utf-8"))
    return [PortfolioPosition(**item) for item in payload]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GlobalGap portfolio macro analysis.")
    subparsers = parser.add_subparsers(dest="command", required=False)

    analyze = subparsers.add_parser("analyze", help="Analyze a portfolio.")
    analyze.add_argument("--portfolio", help="Path to portfolio JSON.")
    analyze.add_argument("--output-json", help="Optional JSON output path.")
    analyze.add_argument("--output-dir", default="./output/globalgap", help="Directory for chart output.")
    analyze.add_argument("--save-charts", action="store_true", help="Save Plotly chart bundle.")
    analyze.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "analyze"
    if command != "analyze":
        parser.error(f"Unsupported command: {command}")

    analyzer = GlobalGapAnalyzer()
    result = analyzer.analyze(_load_positions(getattr(args, "portfolio", None)))
    payload = result.model_dump()

    if getattr(args, "save_charts", False):
        payload["saved_charts"] = save_chart_bundle(result, getattr(args, "output_dir", "./output/globalgap"))

    output = json.dumps(payload, indent=2 if getattr(args, "pretty", False) else None)
    output_path = getattr(args, "output_json", None)
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output + ("\n" if getattr(args, "pretty", False) else ""), encoding="utf-8")
    else:
        print(output)
    return 0

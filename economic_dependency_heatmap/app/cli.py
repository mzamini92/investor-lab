from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional, Union

from economic_dependency_heatmap.app.services.analyzer import EconomicDependencyAnalyzer
from economic_dependency_heatmap.app.services.visualization import save_chart_bundle


def _load_portfolio(path: Union[str, Path]) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict) and "positions" in payload:
        return payload["positions"]
    if not isinstance(payload, list):
        raise ValueError("Portfolio file must be a list or an object with a 'positions' key.")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze portfolio economic dependencies.")
    parser.add_argument("--portfolio", required=True, help="Path to a portfolio JSON file.")
    parser.add_argument("--output-json", help="Optional output path for analysis JSON.")
    parser.add_argument("--save-charts", action="store_true", help="Save HTML chart files.")
    parser.add_argument("--output-dir", default="./output", help="Output directory for charts or saved artifacts.")
    parser.add_argument("--scenario", action="append", default=[], help="Optional scenario name to include. Can be repeated.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the result JSON.")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    analyzer = EconomicDependencyAnalyzer()
    result = analyzer.analyze(_load_portfolio(args.portfolio), selected_scenarios=args.scenario or None).to_dict()

    if args.save_charts:
        result["saved_charts"] = save_chart_bundle(result, args.output_dir)

    output = json.dumps(result, indent=2 if args.pretty else None)
    if args.output_json:
        destination = Path(args.output_json)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output + ("\n" if args.pretty else ""), encoding="utf-8")
    else:
        print(output)
    return 0

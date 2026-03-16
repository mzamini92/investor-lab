from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional, Union

from hedgefund_dependency_engine.app.services.analyzer import HedgefundDependencyAnalyzer
from hedgefund_dependency_engine.app.services.visualization import save_chart_bundle


def _load_portfolio(path: Union[str, Path]) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict) and "positions" in payload:
        return payload["positions"]
    if not isinstance(payload, list):
        raise ValueError("Portfolio file must be a list or an object with a 'positions' key.")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze ETF portfolios with the hedgefund dependency engine.")
    parser.add_argument("--portfolio", required=True, help="Path to a portfolio JSON file.")
    parser.add_argument("--output-json", help="Optional output path for analysis JSON.")
    parser.add_argument("--save-charts", action="store_true", help="Save HTML chart files.")
    parser.add_argument("--output-dir", default="./output", help="Output directory for charts or saved artifacts.")
    parser.add_argument("--scenario", action="append", default=[], help="Optional scenario name to include. Can be repeated.")
    parser.add_argument(
        "--event",
        action="append",
        default=[],
        help="Optional dynamic event in the form event_name or event_name:severity. Can be repeated.",
    )
    parser.add_argument(
        "--headline",
        action="append",
        default=[],
        help="Optional headline or event context text used to infer dynamic scenarios from keywords.",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the result JSON.")
    return parser


def _parse_dynamic_events(raw_events: list[str]) -> list[dict[str, Any]]:
    parsed: list[dict[str, Any]] = []
    for raw_event in raw_events:
        name, separator, severity_text = raw_event.partition(":")
        event_name = name.strip()
        if not event_name:
            continue
        severity = float(severity_text) if separator and severity_text.strip() else 1.0
        parsed.append({"name": event_name, "severity": severity})
    return parsed


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    analyzer = HedgefundDependencyAnalyzer()
    result = analyzer.analyze(
        _load_portfolio(args.portfolio),
        selected_scenarios=args.scenario or None,
        dynamic_events=_parse_dynamic_events(args.event),
        headline_context=" ".join(args.headline).strip() or None,
    ).to_dict()
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

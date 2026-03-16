from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import pandas as pd

from economic_regime_translator.app.config import (
    DEFAULT_CURRENT_SNAPSHOT_FILE,
    DEFAULT_HISTORY_FILE,
    DEFAULT_PRIOR_SNAPSHOT_FILE,
)
from economic_regime_translator.app.models import MacroSnapshot
from economic_regime_translator.app.services.analyzer import EconomicRegimeAnalyzer
from economic_regime_translator.app.services.reporting import build_markdown_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Economic Regime Translator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    classify = subparsers.add_parser("classify")
    classify.add_argument("--snapshot", default=str(DEFAULT_CURRENT_SNAPSHOT_FILE))
    classify.add_argument("--history", default=str(DEFAULT_HISTORY_FILE))
    classify.add_argument("--output-json")
    classify.add_argument("--output-md")
    classify.add_argument("--with-analogs", action="store_true")
    classify.add_argument("--pretty", action="store_true")

    compare = subparsers.add_parser("compare")
    compare.add_argument("--current", default=str(DEFAULT_CURRENT_SNAPSHOT_FILE))
    compare.add_argument("--prior", default=str(DEFAULT_PRIOR_SNAPSHOT_FILE))
    compare.add_argument("--history", default=str(DEFAULT_HISTORY_FILE))
    compare.add_argument("--output-json")
    compare.add_argument("--output-md")
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
    analyzer = EconomicRegimeAnalyzer()

    if args.command == "classify":
        snapshot = MacroSnapshot(**json.loads(Path(args.snapshot).read_text(encoding="utf-8")))
        history = pd.read_csv(args.history) if args.with_analogs or args.history else pd.DataFrame()
        result = analyzer.classify(snapshot, history).to_dict()
        payload = json.dumps(result, indent=2 if args.pretty else None)
        _write_optional(args.output_json, payload + ("\n" if args.pretty else ""))
        _write_optional(args.output_md, build_markdown_report(result))
        if not args.output_json:
            print(payload)
        return 0

    current = MacroSnapshot(**json.loads(Path(args.current).read_text(encoding="utf-8")))
    prior = MacroSnapshot(**json.loads(Path(args.prior).read_text(encoding="utf-8")))
    history = pd.read_csv(args.history)
    result = analyzer.compare(current, prior, history).to_dict()
    payload = json.dumps(result, indent=2 if args.pretty else None)
    _write_optional(args.output_json, payload + ("\n" if args.pretty else ""))
    _write_optional(args.output_md, build_markdown_report(result["current_analysis"]))
    if not args.output_json:
        print(payload)
    return 0

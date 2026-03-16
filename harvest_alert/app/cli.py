from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from harvest_alert.app.config import (
    ACCOUNTS_FILE,
    DEFAULT_SCAN_DATE,
    LOTS_FILE,
    POSITIONS_FILE,
    REPLACEMENTS_FILE,
    TAX_ASSUMPTIONS_FILE,
    TRANSACTIONS_FILE,
)
from harvest_alert.app.models import Account, Position, ReplacementSecurity, TaxAssumptions, TaxLot, Transaction
from harvest_alert.app.services.analyzer import HarvestAlertAnalyzer
from harvest_alert.app.services.reporting import build_markdown_report
from harvest_alert.app.services.visualization import plot_losses, plot_similarity, plot_tax_savings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HarvestAlert")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan")
    scan.add_argument("--accounts", default=str(ACCOUNTS_FILE))
    scan.add_argument("--positions", default=str(POSITIONS_FILE))
    scan.add_argument("--lots", default=str(LOTS_FILE))
    scan.add_argument("--transactions", default=str(TRANSACTIONS_FILE))
    scan.add_argument("--tax-assumptions", default=str(TAX_ASSUMPTIONS_FILE))
    scan.add_argument("--replacements", default=str(REPLACEMENTS_FILE))
    scan.add_argument("--scan-date", default=DEFAULT_SCAN_DATE)
    scan.add_argument("--output-json")
    scan.add_argument("--output-md")
    scan.add_argument("--output-dir", default="./output")
    scan.add_argument("--save-charts", action="store_true")
    scan.add_argument("--pretty", action="store_true")

    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--ticker", required=True)
    evaluate.add_argument("--account", default="taxable_main")
    evaluate.add_argument("--scan-date", default=DEFAULT_SCAN_DATE)
    evaluate.add_argument("--output-json")
    evaluate.add_argument("--pretty", action="store_true")
    return parser


def _read_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_optional(path: Optional[str], content: str) -> None:
    if not path:
        return
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    analyzer = HarvestAlertAnalyzer()

    if args.command == "scan":
        result = analyzer.scan(
            accounts=[Account(**item) for item in _read_json(args.accounts)],
            positions=[Position(**item) for item in _read_json(args.positions)],
            lots=[TaxLot(**item) for item in _read_json(args.lots)],
            transactions=[Transaction(**item) for item in _read_json(args.transactions)],
            tax_assumptions=TaxAssumptions(**_read_json(args.tax_assumptions)),
            replacement_universe=[ReplacementSecurity(**item) for item in _read_json(args.replacements)],
            scan_date=args.scan_date,
        ).to_dict()
        if args.save_charts:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            plot_losses(result["opportunities"]).write_html(str(output_dir / "losses.html"))
            plot_tax_savings(result["opportunities"]).write_html(str(output_dir / "tax_savings.html"))
            plot_similarity(result["opportunities"]).write_html(str(output_dir / "similarity.html"))
        payload = json.dumps(result, indent=2 if args.pretty else None)
        _write_optional(args.output_json, payload + ("\n" if args.pretty else ""))
        _write_optional(args.output_md, build_markdown_report(result))
        if not args.output_json:
            print(payload)
        return 0

    sample = analyzer.sample_scan().to_dict()
    filtered = [item for item in sample["opportunities"] if item["ticker"] == args.ticker.upper() and item["account_id"] == args.account]
    payload = json.dumps({"scan_date": args.scan_date, "opportunities": filtered}, indent=2 if args.pretty else None)
    _write_optional(args.output_json, payload + ("\n" if args.pretty else ""))
    if not args.output_json:
        print(payload)
    return 0

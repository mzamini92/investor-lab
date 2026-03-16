from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional

from earnings_clarity.app.models import EarningsEvent
from earnings_clarity.app.providers.earnings_provider import LocalEarningsEventProvider
from earnings_clarity.app.providers.transcript_provider import LocalTranscriptProvider
from earnings_clarity.app.services.analyzer import EarningsClarityAnalyzer
from earnings_clarity.app.services.parser import parse_raw_transcript
from earnings_clarity.app.services.portfolio import analyze_portfolio_quarter
from earnings_clarity.app.utils.validation import validate_holdings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="EarningsClarity CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_call = subparsers.add_parser("analyze-call", help="Analyze one earnings call.")
    analyze_call.add_argument("--ticker", required=True)
    analyze_call.add_argument("--quarter", required=True)
    analyze_call.add_argument("--transcript", required=True)
    analyze_call.add_argument("--prior")
    analyze_call.add_argument("--event-json")
    analyze_call.add_argument("--output-json")
    analyze_call.add_argument("--output-md")

    analyze_portfolio = subparsers.add_parser("analyze-portfolio", help="Analyze a portfolio for one quarter.")
    analyze_portfolio.add_argument("--holdings", required=True)
    analyze_portfolio.add_argument("--quarter", required=True)
    analyze_portfolio.add_argument("--output-json")
    analyze_portfolio.add_argument("--output-dir")
    return parser


def _load_holdings(path: str) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "holdings" in payload:
        payload = payload["holdings"]
    return payload


def _emit(result: dict[str, Any], output_json: str | None, output_md: str | None = None) -> None:
    content = json.dumps(result, indent=2)
    if output_json:
        Path(output_json).write_text(content + "\n", encoding="utf-8")
    else:
        print(content)
    if output_md:
        markdown = "\n".join(f"- {item}" for item in result["five_point_summary"])
        Path(output_md).write_text(markdown + "\n", encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    analyzer = EarningsClarityAnalyzer()
    if args.command == "analyze-call":
        transcript = parse_raw_transcript(
            ticker=args.ticker.upper(),
            quarter=args.quarter,
            raw_text=Path(args.transcript).read_text(encoding="utf-8"),
        )
        prior = None
        if args.prior:
            prior = parse_raw_transcript(
                ticker=args.ticker.upper(),
                quarter=args.quarter,
                raw_text=Path(args.prior).read_text(encoding="utf-8"),
            )
        if args.event_json:
            event = EarningsEvent(**json.loads(Path(args.event_json).read_text(encoding="utf-8")))
        else:
            event = LocalEarningsEventProvider().get_earnings_event(args.ticker.upper(), args.quarter)
        result = analyzer.analyze_call(earnings_event=event, transcript=transcript, prior_transcript=prior).to_dict()
        _emit(result, args.output_json, args.output_md)
        return 0

    holdings = validate_holdings(_load_holdings(args.holdings))
    results = analyze_portfolio_quarter(analyzer, holdings, args.quarter)
    payload = {"quarter": args.quarter, "results": results}
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    elif args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for item in results:
            Path(output_dir / f"{item['ticker']}_{args.quarter}.json").write_text(
                json.dumps(item, indent=2) + "\n",
                encoding="utf-8",
            )
    else:
        print(json.dumps(payload, indent=2))
    return 0

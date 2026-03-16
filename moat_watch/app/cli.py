from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from moat_watch.app.config import DEFAULT_QUARTER, WATCHLIST_FILE
from moat_watch.app.models import WatchlistItem
from moat_watch.app.services.analyzer import MoatWatchAnalyzer
from moat_watch.app.services.reporting import build_markdown_report
from moat_watch.app.services.visualization import plot_moat_score_history, plot_peer_comparison, plot_signal_radar


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MoatWatch")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze")
    analyze.add_argument("--ticker", required=True)
    analyze.add_argument("--quarter", default=DEFAULT_QUARTER)
    analyze.add_argument("--output-json")
    analyze.add_argument("--output-md")
    analyze.add_argument("--output-dir", default="./output")
    analyze.add_argument("--save-charts", action="store_true")
    analyze.add_argument("--pretty", action="store_true")

    watchlist = subparsers.add_parser("analyze-watchlist")
    watchlist.add_argument("--watchlist", default=str(WATCHLIST_FILE))
    watchlist.add_argument("--quarter", default=DEFAULT_QUARTER)
    watchlist.add_argument("--output-json")
    watchlist.add_argument("--pretty", action="store_true")
    return parser


def _write_optional(path: Optional[str], content: str) -> None:
    if not path:
        return
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    analyzer = MoatWatchAnalyzer()

    if args.command == "analyze":
        result = analyzer.analyze(args.ticker, args.quarter).to_dict()
        if args.save_charts:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            plot_moat_score_history(result["historical_moat_scores"]).write_html(str(output_dir / "moat_history.html"))
            plot_signal_radar(result["signal_breakdown"]).write_html(str(output_dir / "signal_radar.html"))
            plot_peer_comparison(result["peer_comparison"]).write_html(str(output_dir / "peer_comparison.html"))
        payload = json.dumps(result, indent=2 if args.pretty else None)
        _write_optional(args.output_json, payload + ("\n" if args.pretty else ""))
        _write_optional(args.output_md, build_markdown_report(result))
        if not args.output_json:
            print(payload)
        return 0

    watchlist_items = [WatchlistItem(**item) for item in json.loads(Path(args.watchlist).read_text(encoding="utf-8"))]
    result = analyzer.analyze_watchlist(watchlist_items, args.quarter).to_dict()
    payload = json.dumps(result, indent=2 if args.pretty else None)
    _write_optional(args.output_json, payload + ("\n" if args.pretty else ""))
    if not args.output_json:
        print(payload)
    return 0

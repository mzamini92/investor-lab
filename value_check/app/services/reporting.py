from __future__ import annotations

from typing import Any


def build_markdown_report(result: dict[str, Any]) -> str:
    lines = [
        f"# ValueCheck: {result['ticker']}",
        "",
        f"**Verdict:** {result['verdict']['label']}",
        "",
        result["plain_english_summary"]["long_term_holder_paragraph"],
        "",
        "## Current Metrics",
    ]
    for key, value in result["current_metrics"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Watch Items")
    lines.extend(f"- {item}" for item in result["watch_items"])
    lines.append("")
    lines.append("## Caveats")
    lines.extend(f"- {item}" for item in result["caveats"])
    return "\n".join(lines) + "\n"

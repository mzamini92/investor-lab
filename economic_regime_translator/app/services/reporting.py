from __future__ import annotations

from typing import Any


def build_markdown_report(result: dict[str, Any]) -> str:
    summary = result["plain_english_summary"]
    lines = [
        "# Economic Regime Translator",
        "",
        f"## {summary['one_line_label']}",
        "",
        summary["summary_paragraph"],
        "",
        "## Why",
    ]
    lines.extend(f"- {bullet}" for bullet in summary["five_bullet_explanation"])
    lines.append("")
    lines.append("## Watch Items")
    lines.extend(f"- {item}" for item in result["watch_items"])
    lines.append("")
    lines.append("## Risk Flags")
    lines.extend(f"- {item}" for item in result["risk_flags"])
    return "\n".join(lines) + "\n"

from __future__ import annotations

from typing import Any


def build_markdown_report(result: dict[str, Any]) -> str:
    lines = [
        f"# MoatWatch: {result['ticker']}",
        "",
        f"**Quarter:** {result['fiscal_quarter']}",
        f"**Moat health:** {result['moat_health_label']} ({result['moat_health_score']})",
        "",
        result["long_term_takeaway"],
        "",
        "## Key Alerts",
    ]
    lines.extend(f"- {item}" for item in result["alert_flags"])
    lines.append("")
    lines.append("## Watch Items")
    lines.extend(f"- {item}" for item in result["watch_items"])
    return "\n".join(lines) + "\n"

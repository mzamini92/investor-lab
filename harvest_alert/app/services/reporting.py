from __future__ import annotations

from typing import Any


def build_markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# HarvestAlert",
        "",
        f"**Scan date:** {result['scan_date']}",
        f"**Estimated total tax savings:** ${float(result['estimated_total_tax_savings']):,.0f}",
        f"**Estimated total net benefit:** ${float(result['estimated_total_net_benefit']):,.0f}",
        "",
        result["plain_english_summary"]["summary_paragraph"],
        "",
        "## Top Opportunities",
    ]
    for item in result["opportunities"][:5]:
        lines.append(f"- {item['ticker']}: {item['alert_text']}")
    lines.append("")
    lines.append("## Disclaimers")
    lines.extend(f"- {item}" for item in result["disclaimers"])
    return "\n".join(lines) + "\n"

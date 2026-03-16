from __future__ import annotations

from typing import Any


def build_markdown_report(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# True Cost of Investing Summary",
        "",
        f"- Portfolio value: ${summary['portfolio_value']:,.0f}",
        f"- Hidden annual drag: {summary['total_hidden_annual_drag_rate']:.2%}",
        f"- Gross ending value: ${summary['gross_ending_value']:,.0f}",
        f"- Net ending value: ${summary['net_ending_value']:,.0f}",
        f"- Lifetime dollars lost: ${summary['total_30_year_dollars_lost']:,.0f}",
        f"- Biggest cost category: {summary['biggest_cost_category'].replace('_', ' ')}",
        "",
        "## Insights",
    ]
    lines.extend(f"- {item}" for item in result["insights"])
    lines.append("")
    lines.append("## Recommendations")
    lines.extend(f"- {item}" for item in result["recommendations"])
    return "\n".join(lines) + "\n"

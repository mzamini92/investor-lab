from __future__ import annotations

from true_cost_of_investing.app.models import ComparisonResult, CostAnalysisResult


def compare_results(current: CostAnalysisResult, alternative: CostAnalysisResult) -> ComparisonResult:
    current_end = current.projected_ending_values["net_ending_value"]
    alternative_end = alternative.projected_ending_values["net_ending_value"]
    savings = alternative_end - current_end

    savings_by_category = {}
    current_categories = {row["category"]: row["attributable_ending_value_loss"] for row in current.dollars_lost_by_category}
    alternative_categories = {row["category"]: row["attributable_ending_value_loss"] for row in alternative.dollars_lost_by_category}
    for category in sorted(set(current_categories) | set(alternative_categories)):
        savings_by_category[category] = round(current_categories.get(category, 0.0) - alternative_categories.get(category, 0.0), 2)

    insights = [
        f"The alternative portfolio preserves about ${savings:,.0f} more ending wealth over the modeled horizon."
    ]
    recommendations = [
        "Focus first on the largest friction categories in the current portfolio before fine-tuning smaller costs."
    ]
    return ComparisonResult(
        current=current,
        alternative=alternative,
        projected_savings={
            "ending_value_savings": round(savings, 2),
            "net_value_current": round(current_end, 2),
            "net_value_alternative": round(alternative_end, 2),
            "savings_by_category": savings_by_category,
        },
        insights=insights,
        recommendations=recommendations,
    )

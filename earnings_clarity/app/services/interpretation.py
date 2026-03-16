from __future__ import annotations

from earnings_clarity.app.utils.constants import JARGON_EXPLANATIONS


def classify_thesis_status(headline: dict[str, object], guidance_view: dict[str, object], tone_shift: dict[str, object]) -> str:
    caution_score = float(guidance_view["guidance_caution_score"])
    positive_score = float(guidance_view["guidance_positive_score"])
    tone_label = str(tone_shift["tone_shift_label"])
    headline_label = str(headline["headline_classification"])
    if caution_score >= 5.0 and tone_label == "more_cautious":
        return "weakening"
    if positive_score >= caution_score + 2.0 and headline_label == "beat":
        return "improving"
    if caution_score > positive_score:
        return "mixed"
    return "intact"


def build_long_term_interpretation(
    *,
    company_name: str,
    headline: dict[str, object],
    guidance_view: dict[str, object],
    tone_shift: dict[str, object],
    top_topics: list[dict[str, object]],
) -> dict[str, object]:
    thesis_status = classify_thesis_status(headline, guidance_view, tone_shift)
    watch_items = [str(topic["topic"]) for topic in top_topics[:3]]
    headline_label = str(headline["headline_classification"])
    guidance_label = str(guidance_view["guidance_label"])
    tone_label = str(tone_shift["tone_shift_label"])

    if thesis_status == "weakening":
        takeaway = (
            f"For a steady long-term holder, this quarter does not automatically break the {company_name} thesis, "
            "but it did add evidence that near-term execution and visibility are worsening."
        )
    elif thesis_status == "improving":
        takeaway = (
            f"For a DCA investor, this quarter looked supportive of the long-term business story, "
            "because the operating tone and headline results both improved."
        )
    elif thesis_status == "mixed":
        takeaway = (
            f"For a long-term holder, this quarter looked mixed: the headline result was {headline_label}, "
            f"but the forward commentary was {guidance_label} and tone was {tone_label.replace('_', ' ')}."
        )
    else:
        takeaway = (
            f"For a long-term holder, this quarter looked more like execution noise than a thesis break, "
            "but the next quarter still matters for confirming the trend."
        )

    if watch_items:
        takeaway += f" Watch {', '.join(watch_items[:3])} next quarter."

    explained_jargon = [
        f"{term}: {meaning}"
        for term, meaning in JARGON_EXPLANATIONS.items()
        if any(term in str(topic.get('topic', '')).lower() for topic in top_topics)
    ]
    return {
        "long_term_takeaway": takeaway,
        "thesis_status": thesis_status,
        "next_quarter_watch_items": watch_items,
        "jargon_notes": explained_jargon[:3],
    }

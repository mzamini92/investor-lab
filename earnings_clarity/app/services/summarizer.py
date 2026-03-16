from __future__ import annotations

from earnings_clarity.app.models import EarningsEvent


def build_five_point_summary(
    *,
    event: EarningsEvent,
    headline: dict[str, object],
    guidance_view: dict[str, object],
    risk_flag: dict[str, object],
    tone_shift: dict[str, object],
    interpretation: dict[str, object],
) -> list[str]:
    headline_bullet = (
        f"Headline: {event.company_name} {headline['headline_classification']} expectations, "
        f"with revenue {headline['revenue_classification']} and EPS {headline['eps_classification']} versus consensus."
    )
    future_bullet = (
        f"Future outlook: Management commentary looked {guidance_view['guidance_label']}, "
        f"with positive score {guidance_view['guidance_positive_score']} and caution score {guidance_view['guidance_caution_score']}."
    )
    risk_bullet = (
        f"Key risk: {risk_flag['label']} was the most important concern flagged, based on repeated caution language and analyst focus."
    )
    tone_bullet = (
        f"Tone shift: Compared with the prior quarter, management sounded {str(tone_shift['tone_shift_label']).replace('_', ' ')}."
    )
    dca_bullet = f"Long-term holder takeaway: {interpretation['long_term_takeaway']}"
    return [headline_bullet, future_bullet, risk_bullet, tone_bullet, dca_bullet]


def build_extended_summary(event: EarningsEvent, five_point_summary: list[str]) -> dict[str, str]:
    short_paragraph = " ".join(
        [
            five_point_summary[0].replace("Headline: ", ""),
            five_point_summary[1].replace("Future outlook: ", ""),
            five_point_summary[4].replace("Long-term holder takeaway: ", ""),
        ]
    )
    app_card = f"{event.ticker} — {event.quarter}\n" + "\n".join(f"{index + 1}. {bullet}" for index, bullet in enumerate(five_point_summary))
    email_ready = (
        f"{event.company_name} {event.quarter} EarningsClarity\n\n"
        + "\n".join(f"- {bullet}" for bullet in five_point_summary)
    )
    return {
        "short_paragraph": short_paragraph,
        "app_card": app_card,
        "email_ready": email_ready,
    }

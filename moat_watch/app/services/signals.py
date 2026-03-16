from __future__ import annotations

from typing import Any

from moat_watch.app.models import SignalResult
from moat_watch.app.utils.math_utils import clamp


def _status_from_score(score: float, positive: str, neutral: str, negative: str) -> str:
    if score >= 65:
        return positive
    if score <= 40:
        return negative
    return neutral


def _direction(change: float | None) -> str:
    if change is None:
        return "unknown"
    if change > 0:
        return "improving"
    if change < 0:
        return "weakening"
    return "stable"


def build_signals(context: dict[str, Any], commentary_findings: dict[str, Any]) -> list[SignalResult]:
    signals: list[SignalResult] = []

    gm_change = context.get("gross_margin_change_bps_qoq")
    gm_score = 50.0
    if gm_change is not None:
        gm_score = clamp(50.0 + (gm_change / 6.0), 0.0, 100.0)
    signals.append(
        SignalResult(
            signal_name="gross_margin_trajectory",
            current_status=_status_from_score(gm_score, "expanding", "stable", "compressing"),
            change_direction=_direction(gm_change),
            strength_score=round(gm_score, 2),
            evidence=f"Gross margin change QoQ: {0.0 if gm_change is None else gm_change:.0f} bps.",
            value=gm_change,
        )
    )

    roic_change = context.get("roic_spread_change_qoq")
    roic_score = clamp(50.0 + ((roic_change or 0.0) * 500.0) + ((context.get("roic_wacc_spread") or 0.0) * 300.0), 0.0, 100.0)
    signals.append(
        SignalResult(
            signal_name="roic_spread",
            current_status=_status_from_score(roic_score, "widening spread", "stable spread", "narrowing spread"),
            change_direction=_direction(roic_change),
            strength_score=round(roic_score, 2),
            evidence=f"ROIC spread is {(context.get('roic_wacc_spread') or 0.0):.1%} with QoQ change {(roic_change or 0.0):+.1%}.",
            value=context.get("roic_wacc_spread"),
        )
    )

    price_realization = context.get("price_realization") or 0.0
    volume_growth = context.get("volume_growth")
    same_store_sales = context.get("same_store_sales")
    pricing_score = 50.0 + (price_realization * 400.0)
    if volume_growth is not None:
        pricing_score += volume_growth * 120.0
    if same_store_sales is not None:
        pricing_score += same_store_sales * 80.0
    pricing_score = clamp(pricing_score, 0.0, 100.0)
    signals.append(
        SignalResult(
            signal_name="pricing_power",
            current_status=_status_from_score(pricing_score, "pricing power intact", "mixed pricing power", "price-sensitive demand"),
            change_direction=_direction(context.get("asp_change_qoq")),
            strength_score=round(pricing_score, 2),
            evidence="Pricing power blends price realization, volume stability, and same-store-sales support.",
            value=price_realization,
        )
    )

    share_change = context.get("market_share_change_qoq")
    share_score = clamp(50.0 + ((share_change or 0.0) * 3000.0), 0.0, 100.0)
    signals.append(
        SignalResult(
            signal_name="market_share",
            current_status=_status_from_score(share_score, "gaining share", "holding share", "losing share"),
            change_direction=_direction(share_change),
            strength_score=round(share_score, 2),
            evidence=f"Market share change QoQ: {(share_change or 0.0):+.2%}.",
            value=share_change,
        )
    )

    innovation_delta = context.get("r_and_d_intensity_change_qoq")
    innovation_score = clamp(
        50.0 + ((context.get("r_and_d_as_pct_revenue") or 0.0) * 350.0) + ((innovation_delta or 0.0) * 1200.0),
        0.0,
        100.0,
    )
    signals.append(
        SignalResult(
            signal_name="innovation_reinvestment",
            current_status=_status_from_score(innovation_score, "reinvesting to extend moat", "steady reinvestment", "underinvesting"),
            change_direction=_direction(innovation_delta),
            strength_score=round(innovation_score, 2),
            evidence="Innovation signal blends R&D intensity and whether reinvestment is strengthening or fading.",
            value=context.get("r_and_d_as_pct_revenue"),
        )
    )

    sales_eff_change = context.get("sales_efficiency_change_qoq")
    sales_eff_score = clamp(50.0 + ((context.get("sales_efficiency_proxy") or 0.0) * 12.0) + ((sales_eff_change or 0.0) * 20.0), 0.0, 100.0)
    signals.append(
        SignalResult(
            signal_name="sales_efficiency",
            current_status=_status_from_score(sales_eff_score, "efficient customer economics", "stable efficiency", "slipping efficiency"),
            change_direction=_direction(sales_eff_change),
            strength_score=round(sales_eff_score, 2),
            evidence="Sales efficiency uses LTV/CAC when available, otherwise an operating-margin-to-S&M proxy.",
            value=context.get("sales_efficiency_proxy"),
        )
    )

    commentary_score = commentary_findings["pressure_score"]
    signals.append(
        SignalResult(
            signal_name="commentary_pressure",
            current_status=_status_from_score(commentary_score, "management tone supportive", "mixed management tone", "more defensive tone"),
            change_direction="improving" if commentary_score >= 60 else ("weakening" if commentary_score <= 40 else "stable"),
            strength_score=round(commentary_score, 2),
            evidence="Commentary score reflects explicit mentions of competition, promotions, share gains, and innovation strength.",
            value=commentary_score,
        )
    )
    return signals

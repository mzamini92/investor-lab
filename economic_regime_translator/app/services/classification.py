from __future__ import annotations

from typing import Any


def classify_regime(indicator_states: dict[str, Any], scorecard: dict[str, float]) -> dict[str, Any]:
    growth = scorecard["growth_score"]
    inflation = scorecard["inflation_score"]
    policy = scorecard["policy_restrictiveness_score"]
    credit = scorecard["credit_stress_score"]
    earnings = scorecard["earnings_momentum_score"]
    recession = scorecard["recession_risk_score"]
    curve = scorecard["curve_warning_score"]

    if recession >= 80 and credit >= 70 and growth <= 35:
        label = "Full recession contraction"
    elif credit >= 75:
        label = "Credit stress regime"
    elif inflation >= 70 and growth <= 45:
        label = "Stagflation risk regime"
    elif growth <= 40 and policy >= 65 and recession >= 60:
        label = "Growth scare under restrictive policy"
    elif earnings <= 35 and growth <= 50:
        label = "Earnings recession risk"
    elif inflation <= 50 and growth >= 45 and policy >= 55 and credit <= 45 and recession <= 55:
        label = "Disinflationary soft landing"
    elif growth >= 70 and policy <= 45 and inflation >= 45:
        label = "Early-cycle reflation"
    elif growth >= 65 and policy >= 60 and inflation >= 55:
        label = "Re-acceleration under tight policy"
    elif growth >= 58 and credit <= 40 and earnings >= 55:
        label = "Mid-cycle expansion"
    else:
        label = "Late-cycle slowdown"

    sub_labels = [
        indicator_states["inflation_trend"],
        indicator_states["labor_trend"],
        indicator_states["curve_state"],
        indicator_states["earnings_state"],
    ]
    drivers = []
    if indicator_states["inflation_trend"] == "cooling":
        drivers.append("Inflation is cooling versus its recent trend.")
    if indicator_states["curve_state"] in {"inverted", "deeply_inverted"}:
        drivers.append("The yield curve remains inverted, which raises cycle caution.")
    if indicator_states["credit_state"] != "benign":
        drivers.append("Credit spreads are no longer benign.")
    if indicator_states["earnings_state"] == "deteriorating":
        drivers.append("Earnings revisions are deteriorating.")
    if growth >= 55:
        drivers.append("Activity indicators still point to resilient growth.")
    if not drivers:
        drivers.append("Macro signals are mixed, pointing to a late-cycle but not yet fully stressed environment.")

    return {
        "regime_label": label,
        "sub_regime_labels": sub_labels,
        "primary_drivers": drivers,
        "risk_flags": [
            flag
            for flag, condition in {
                "Curve inversion still argues for caution.": curve >= 60,
                "Credit conditions could tighten further.": credit >= 55,
                "Earnings revision breadth remains fragile.": earnings <= 45,
                "Policy remains restrictive for this stage of the cycle.": policy >= 60,
            }.items()
            if condition
        ],
        "watch_items": [
            item
            for item, condition in {
                "Watch whether earnings revisions stabilize.": earnings <= 55,
                "Watch whether inflation keeps cooling without a growth break.": indicator_states["inflation_trend"] == "cooling",
                "Watch whether the curve steepens because growth improves or because stress is rising.": curve >= 55,
                "Watch whether spreads widen further from here.": credit >= 45,
            }.items()
            if condition
        ],
    }

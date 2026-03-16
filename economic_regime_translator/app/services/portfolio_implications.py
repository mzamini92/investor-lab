from __future__ import annotations

from typing import Any


IMPLICATIONS = {
    "Disinflationary soft landing": {
        "favorable_conditions": ["Broad equities if revisions stabilize", "Quality duration if inflation continues cooling"],
        "unfavorable_conditions": ["Deep cyclicals if growth rolls over", "Lower-quality credit if spreads widen again"],
        "watch_items": ["Earnings revisions", "Labor cooling without a jump in layoffs"],
        "risk_flags": ["A soft landing can still fail if earnings weaken faster than inflation cools."],
        "paragraph": "In this regime, risk assets can hold up if growth slows only modestly and revisions stop worsening. Long-term investors should watch whether disinflation continues without a deeper growth break.",
    },
    "Growth scare under restrictive policy": {
        "favorable_conditions": ["Defensive balance-sheet quality", "Potential support for duration if growth weakens more"],
        "unfavorable_conditions": ["Highly cyclical equities", "Lower-quality credit"],
        "watch_items": ["Credit spreads", "Further earnings estimate cuts"],
        "risk_flags": ["Restrictive policy leaves little room for disappointment."],
        "paragraph": "Similar periods often punished economically sensitive assets before the policy outlook shifted. The key question is whether weaker growth becomes severe enough to change the policy path.",
    },
    "Credit stress regime": {
        "favorable_conditions": ["Higher-quality balance sheets", "Safer duration assets if stress deepens"],
        "unfavorable_conditions": ["Credit-sensitive assets", "Smaller or highly levered equities"],
        "watch_items": ["Spread widening", "Liquidity and funding conditions"],
        "risk_flags": ["Credit deterioration can spill into the real economy quickly."],
        "paragraph": "When credit is the main problem, balance-sheet quality matters more than broad market beta. Long-term investors should focus on whether stress remains contained or starts impairing growth and earnings materially.",
    },
}


def build_portfolio_implications(regime_label: str) -> dict[str, Any]:
    fallback = {
        "favorable_conditions": ["Diversified quality exposure", "Flexibility while signals remain mixed"],
        "unfavorable_conditions": ["Crowded one-way macro bets"],
        "watch_items": ["Inflation trend", "Growth resilience", "Earnings revisions"],
        "risk_flags": ["Mixed signals reduce conviction in any single macro narrative."],
        "paragraph": "The current regime is mixed enough that investors should focus on resilience rather than precision timing. The next move in earnings, inflation, and credit will matter more than any one data print.",
    }
    return IMPLICATIONS.get(regime_label, fallback)

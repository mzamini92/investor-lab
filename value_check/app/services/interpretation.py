from __future__ import annotations

from typing import Any


def build_long_term_interpretation(
    *,
    ticker: str,
    asset_type: str,
    verdict_label: str,
    current_metrics: dict[str, Any],
    peer_rows: list[dict[str, Any]],
    caveats: list[str],
) -> tuple[str, list[str], list[str], dict[str, Any]]:
    spread = current_metrics.get("treasury_relative_fcf_spread")
    watch_items: list[str] = []
    caution_flags = caveats[:]

    if spread is not None and spread < 0:
        watch_items.append("Watch whether future cash-flow growth is strong enough to justify a lower cash-flow yield than Treasuries.")
    if any(row.get("peer_interpretation") == "premium" for row in peer_rows):
        watch_items.append("Peer premiums mean future returns may depend more heavily on continued flawless execution.")
    if verdict_label in {"expensive", "extremely expensive"}:
        watch_items.append("Elevated expectations leave less room for business stumbles than usual.")
    if asset_type == "etf":
        watch_items.append("ETF valuation proxies are useful, but less precise than single-stock fundamentals.")

    if verdict_label == "cheap":
        takeaway = f"{ticker} screens as cheap on the blended valuation view. That does not guarantee upside, but expectations look relatively undemanding."
    elif verdict_label == "fair":
        takeaway = f"{ticker} looks roughly fair on this framework. For a steady DCA investor, valuation is not a strong headwind or tailwind here."
    elif verdict_label == "slightly expensive":
        takeaway = f"{ticker} looks somewhat expensive, but not at a clear extreme. Long-term buyers should expect future returns to lean more on execution than multiple expansion."
    elif verdict_label == "expensive":
        takeaway = f"{ticker} looks expensive versus history and/or peers. That does not mean it must fall, but it does mean expectations are already high."
    else:
        takeaway = f"{ticker} looks extremely expensive on this framework. For a long-term DCA investor, patience and sizing discipline matter more than usual."

    bullets = [
        f"Verdict: {verdict_label.replace('_', ' ')}.",
        "The view combines own-history percentiles, peer premiums, and Treasury-relative cash-flow context.",
        "High-quality businesses can stay expensive, but rich starting valuations raise the bar for future results.",
        "Mixed or missing metrics reduce confidence, especially for ETFs and unprofitable businesses.",
        "This is valuation context, not a buy or sell call.",
    ]
    return takeaway, watch_items, caution_flags, {
        "short_verdict_line": takeaway,
        "five_bullet_explanation": bullets,
        "long_term_holder_paragraph": takeaway,
    }

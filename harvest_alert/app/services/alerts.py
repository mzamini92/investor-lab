from __future__ import annotations


def build_alert_text(
    *,
    ticker: str,
    harvestable_loss: float,
    estimated_tax_savings: float,
    replacement_ticker: str | None,
    hold_days: int,
    risk_summary: str,
    drift_summary: str,
) -> str:
    if replacement_ticker:
        return (
            f"{ticker} is down ${harvestable_loss:,.0f}. Selling and replacing it with {replacement_ticker} "
            f"for {hold_days} days could create an estimated ${estimated_tax_savings:,.0f} tax benefit. "
            f"Wash-sale screen: {risk_summary}. Expected drift: {drift_summary}"
        )
    return (
        f"{ticker} is down ${harvestable_loss:,.0f}, but HarvestAlert did not find a clean temporary replacement. "
        f"Wash-sale screen: {risk_summary}. Manual review may be needed."
    )

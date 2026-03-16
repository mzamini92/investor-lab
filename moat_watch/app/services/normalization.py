from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from moat_watch.app.models import QuarterlyMetrics
from moat_watch.app.utils.math_utils import safe_change, safe_divide, safe_pct_change


def _quarter_label_from_row(row: pd.Series) -> str:
    return f"{int(row['fiscal_year'])}Q{int(row['fiscal_quarter'])}"


def build_quarter_context(
    current: QuarterlyMetrics,
    prior_quarter: QuarterlyMetrics | None,
    prior_year_quarter: QuarterlyMetrics | None,
) -> dict[str, Any]:
    gross_margin = safe_divide(current.gross_profit, current.revenue)
    roic_spread = current.roic - current.estimated_wacc
    r_and_d_pct = safe_divide(current.r_and_d_expense, current.revenue)
    sales_marketing_pct = safe_divide(current.sales_and_marketing_expense, current.revenue)
    capex_pct = safe_divide(current.capex, current.revenue)

    prior_gross_margin = safe_divide(prior_quarter.gross_profit, prior_quarter.revenue) if prior_quarter else None
    prior_year_gross_margin = safe_divide(prior_year_quarter.gross_profit, prior_year_quarter.revenue) if prior_year_quarter else None
    prior_roic_spread = (prior_quarter.roic - prior_quarter.estimated_wacc) if prior_quarter else None
    prior_year_roic_spread = (prior_year_quarter.roic - prior_year_quarter.estimated_wacc) if prior_year_quarter else None
    prior_r_and_d_pct = safe_divide(prior_quarter.r_and_d_expense, prior_quarter.revenue) if prior_quarter else None
    prior_sales_marketing_pct = safe_divide(prior_quarter.sales_and_marketing_expense, prior_quarter.revenue) if prior_quarter else None
    prior_capex_pct = safe_divide(prior_quarter.capex, prior_quarter.revenue) if prior_quarter else None

    market_share_change_qoq = safe_change(current.market_share, prior_quarter.market_share if prior_quarter else None)
    market_share_change_yoy = safe_change(current.market_share, prior_year_quarter.market_share if prior_year_quarter else None)
    asp_change_qoq = safe_pct_change(current.average_selling_price, prior_quarter.average_selling_price if prior_quarter else None)
    revenue_per_unit_change_qoq = safe_pct_change(current.revenue_per_unit, prior_quarter.revenue_per_unit if prior_quarter else None)
    volume_growth_change_qoq = safe_change(current.volume_growth, prior_quarter.volume_growth if prior_quarter else None)

    return {
        "ticker": current.ticker,
        "company_name": current.company_name,
        "sector": current.sector,
        "industry": current.industry,
        "quarter": current.quarter_label,
        "gross_margin": gross_margin,
        "gross_margin_change_bps_qoq": None if gross_margin is None or prior_gross_margin is None else (gross_margin - prior_gross_margin) * 10000.0,
        "gross_margin_change_bps_yoy": None if gross_margin is None or prior_year_gross_margin is None else (gross_margin - prior_year_gross_margin) * 10000.0,
        "operating_margin": current.operating_margin,
        "operating_margin_change_bps_qoq": safe_change(current.operating_margin, prior_quarter.operating_margin if prior_quarter else None),
        "free_cash_flow": current.free_cash_flow,
        "roic": current.roic,
        "roic_wacc_spread": roic_spread,
        "roic_spread_change_qoq": safe_change(roic_spread, prior_roic_spread),
        "roic_spread_change_yoy": safe_change(roic_spread, prior_year_roic_spread),
        "r_and_d_as_pct_revenue": r_and_d_pct,
        "r_and_d_intensity_change_qoq": safe_change(r_and_d_pct, prior_r_and_d_pct),
        "sales_marketing_as_pct_revenue": sales_marketing_pct,
        "sales_efficiency_proxy": current.ltv_to_cac if current.ltv_to_cac is not None else (
            None if sales_marketing_pct in {None, 0} else current.operating_margin / sales_marketing_pct
        ),
        "sales_efficiency_change_qoq": safe_change(
            current.ltv_to_cac if current.ltv_to_cac is not None else (None if sales_marketing_pct in {None, 0} else current.operating_margin / sales_marketing_pct),
            prior_quarter.ltv_to_cac if prior_quarter and prior_quarter.ltv_to_cac is not None else (
                None if prior_quarter is None or prior_sales_marketing_pct in {None, 0} else prior_quarter.operating_margin / prior_sales_marketing_pct
            ),
        ),
        "same_store_sales": current.same_store_sales,
        "average_selling_price": current.average_selling_price,
        "asp_change_qoq": asp_change_qoq,
        "revenue_per_unit_change_qoq": revenue_per_unit_change_qoq,
        "volume_growth": current.volume_growth,
        "volume_growth_change_qoq": volume_growth_change_qoq,
        "price_realization": current.price_realization,
        "market_share": current.market_share,
        "market_share_change_qoq": market_share_change_qoq,
        "market_share_change_yoy": market_share_change_yoy,
        "capex_as_pct_revenue": capex_pct,
        "capex_intensity_change_qoq": safe_change(capex_pct, prior_capex_pct),
        "inventory_growth": current.inventory_growth,
        "receivables_growth": current.receivables_growth,
        "customer_acquisition_cost": current.customer_acquisition_cost,
        "ltv_to_cac": current.ltv_to_cac,
    }


def find_reference_rows(history_df: pd.DataFrame, quarter: str) -> tuple[pd.Series, Optional[pd.Series], Optional[pd.Series]]:
    ordered = history_df.copy()
    ordered["quarter_label"] = ordered.apply(_quarter_label_from_row, axis=1)
    ordered["quarter_sort"] = ordered["fiscal_year"] * 10 + ordered["fiscal_quarter"]
    current_rows = ordered.loc[ordered["quarter_label"].str.upper() == quarter.upper()]
    if current_rows.empty:
        raise ValueError(f"Quarter {quarter} not found in history.")
    current_row = current_rows.iloc[0]
    prior_rows = ordered.loc[ordered["quarter_sort"] < current_row["quarter_sort"]].sort_values("quarter_sort")
    prior_row = prior_rows.iloc[-1] if not prior_rows.empty else None
    prior_yoy_rows = ordered.loc[
        (ordered["fiscal_quarter"] == current_row["fiscal_quarter"]) & (ordered["fiscal_year"] == current_row["fiscal_year"] - 1)
    ]
    prior_yoy_row = prior_yoy_rows.iloc[-1] if not prior_yoy_rows.empty else None
    return current_row, prior_row, prior_yoy_row

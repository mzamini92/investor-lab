import pandas as pd

from moat_watch.app.services.peers import compare_against_peers


def test_peer_comparison_flags_relative_strength() -> None:
    context = {
        "gross_margin": 0.70,
        "roic_wacc_spread": 0.18,
        "r_and_d_as_pct_revenue": 0.12,
        "market_share_change_qoq": 0.01,
        "price_realization": 0.03,
    }
    peer_df = pd.DataFrame(
        [
            {"ticker": "P1", "company_name": "Peer1", "sector": "Tech", "industry": "Software", "fiscal_year": 2025, "fiscal_quarter": 2, "revenue": 100, "gross_profit": 60, "operating_margin": 0.25, "free_cash_flow": 15, "invested_capital": 70, "roic": 0.18, "estimated_wacc": 0.09, "r_and_d_expense": 9, "sales_and_marketing_expense": 18, "capex": 4, "market_share": 0.20, "price_realization": 0.01},
            {"ticker": "P2", "company_name": "Peer2", "sector": "Tech", "industry": "Software", "fiscal_year": 2025, "fiscal_quarter": 2, "revenue": 120, "gross_profit": 74, "operating_margin": 0.27, "free_cash_flow": 18, "invested_capital": 80, "roic": 0.19, "estimated_wacc": 0.09, "r_and_d_expense": 10, "sales_and_marketing_expense": 20, "capex": 5, "market_share": 0.22, "price_realization": 0.015},
        ]
    )
    rows = compare_against_peers(context, peer_df)
    gross_margin = next(item for item in rows if item["metric"] == "gross_margin")
    assert gross_margin["peer_interpretation"] in {"stronger than peers", "near peer median"}

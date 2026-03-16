from __future__ import annotations

import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from earnings_clarity.app.config import DEFAULT_SAMPLE_HOLDINGS as DEFAULT_EARNINGS_SAMPLE_HOLDINGS
from earnings_clarity.app.providers.earnings_provider import LocalEarningsEventProvider
from earnings_clarity.app.services.analyzer import EarningsClarityAnalyzer
from earnings_clarity.app.services.portfolio import analyze_portfolio_quarter as analyze_earnings_portfolio_quarter
from earnings_clarity.app.utils.validation import validate_holdings as validate_earnings_holdings
from economic_dependency_heatmap.app.config import DEFAULT_SAMPLE_PORTFOLIO as DEFAULT_DEPENDENCY_SAMPLE_PORTFOLIO
from economic_dependency_heatmap.app.config import ETF_HOLDINGS_DIR as DEPENDENCY_HOLDINGS_DIR
from economic_dependency_heatmap.app.providers.csv_provider import CSVDependencyDataProvider
from economic_dependency_heatmap.app.services.analyzer import EconomicDependencyAnalyzer
from economic_dependency_heatmap.app.services.visualization import (
    build_network_figure,
    plot_dependency_heatmap,
    plot_domicile_vs_revenue as plot_dependency_domicile_vs_revenue,
    plot_macro_dependency_ranking,
    plot_scenario_dashboard,
    plot_world_map as plot_dependency_world_map,
)
from economic_regime_translator.app.config import DEFAULT_CURRENT_SNAPSHOT_FILE as DEFAULT_REGIME_CURRENT_FILE
from economic_regime_translator.app.config import DEFAULT_HISTORY_FILE as DEFAULT_REGIME_HISTORY_FILE
from economic_regime_translator.app.config import DEFAULT_PRIOR_SNAPSHOT_FILE as DEFAULT_REGIME_PRIOR_FILE
from economic_regime_translator.app.models import MacroSnapshot as RegimeMacroSnapshot
from economic_regime_translator.app.services.analyzer import EconomicRegimeAnalyzer
from economic_regime_translator.app.services.visualization import (
    build_analog_similarity_chart as build_regime_analog_similarity_chart,
    build_score_bar_chart as build_regime_score_bar_chart,
    build_transition_chart as build_regime_transition_chart,
)
from etf_catalog.fetcher import load_etf_catalog
from etf_overlap.config import DEFAULT_DATA_DIR
from etf_overlap.config import DEFAULT_SAMPLE_PORTFOLIO
from etf_overlap.engine import PortfolioAnalyzer
from etf_overlap.providers.live_provider import LiveHybridHoldingsProvider
from etf_overlap.visualization import plot_overlap_heatmap, plot_sector_exposure_chart, plot_top_holdings_bar
from global_etf_exposure_map.app.config import DEFAULT_SAMPLE_PORTFOLIO as DEFAULT_GLOBAL_SAMPLE_PORTFOLIO
from global_etf_exposure_map.app.config import ETF_HOLDINGS_DIR
from global_etf_exposure_map.app.providers.csv_provider import CSVHoldingsProvider as GlobalCSVHoldingsProvider
from global_etf_exposure_map.app.services.analyzer import GlobalExposureAnalyzer
from global_etf_exposure_map.app.services.visualization import (
    plot_country_concentration,
    plot_currency_exposure,
    plot_domicile_vs_revenue,
    plot_region_exposure,
    plot_world_choropleth,
)
from globalgap.app.analyzer import GlobalGapAnalyzer
from globalgap.app.config import SAMPLE_PORTFOLIO_FILE as GLOBALGAP_SAMPLE_PORTFOLIO_FILE
from globalgap.app.models import PortfolioPosition as GlobalGapPortfolioPosition
from globalgap.app.visualization import (
    build_analog_bar_chart as build_globalgap_analog_bar_chart,
    build_dollar_cycle_chart as build_globalgap_dollar_cycle_chart,
    build_exposure_pie as build_globalgap_exposure_pie,
    build_simulation_chart as build_globalgap_simulation_chart,
    build_valuation_history_chart as build_globalgap_valuation_history_chart,
)
from hedgefund_dependency_engine.app.config import DEFAULT_DYNAMIC_EVENTS
from hedgefund_dependency_engine.app.config import DEFAULT_SAMPLE_PORTFOLIO as DEFAULT_HF_SAMPLE_PORTFOLIO
from hedgefund_dependency_engine.app.config import ETF_HOLDINGS_DIR as HF_HOLDINGS_DIR
from hedgefund_dependency_engine.app.news.rss_provider import GoogleNewsRSSProvider
from hedgefund_dependency_engine.app.providers.csv_provider import CSVEngineDataProvider
from hedgefund_dependency_engine.app.services.analyzer import HedgefundDependencyAnalyzer
from hedgefund_dependency_engine.app.services.live_news import headlines_to_context, suggest_dynamic_events_from_headlines
from hedgefund_dependency_engine.app.services.visualization import (
    build_network_figure as build_hf_network_figure,
    plot_company_exposure_bar as plot_hf_company_exposure_bar,
    plot_country_exposure_chart as plot_hf_country_exposure_chart,
    plot_dependency_heatmap as plot_hf_dependency_heatmap,
    plot_domicile_vs_revenue as plot_hf_domicile_vs_revenue,
    plot_scenario_impact_chart as plot_hf_scenario_impact_chart,
    plot_world_map as plot_hf_world_map,
)
from true_cost_of_investing.app.config import (
    DEFAULT_ALTERNATIVE_PORTFOLIO_FILE as DEFAULT_COST_ALTERNATIVE_PORTFOLIO_FILE,
)
from true_cost_of_investing.app.config import DEFAULT_ASSUMPTIONS_FILE as DEFAULT_COST_ASSUMPTIONS_FILE
from true_cost_of_investing.app.config import DEFAULT_PORTFOLIO_FILE as DEFAULT_COST_PORTFOLIO_FILE
from true_cost_of_investing.app.models import HoldingInput as CostHoldingInput
from true_cost_of_investing.app.models import PortfolioAssumptions as CostPortfolioAssumptions
from true_cost_of_investing.app.services.analyzer import TrueCostAnalyzer
from true_cost_of_investing.app.services.visualization import (
    plot_comparison_chart as plot_cost_comparison_chart,
    plot_cumulative_loss_timeline as plot_cost_cumulative_loss_timeline,
    plot_gross_vs_net_timeline as plot_cost_gross_vs_net_timeline,
    plot_stacked_cost_breakdown as plot_cost_stacked_cost_breakdown,
)
from harvest_alert.app.config import (
    ACCOUNTS_FILE as HARVEST_ACCOUNTS_FILE,
    LOTS_FILE as HARVEST_LOTS_FILE,
    POSITIONS_FILE as HARVEST_POSITIONS_FILE,
    REPLACEMENTS_FILE as HARVEST_REPLACEMENTS_FILE,
    TAX_ASSUMPTIONS_FILE as HARVEST_TAX_ASSUMPTIONS_FILE,
    TRANSACTIONS_FILE as HARVEST_TRANSACTIONS_FILE,
)
from harvest_alert.app.models import Account as HarvestAccount
from harvest_alert.app.models import Position as HarvestPosition
from harvest_alert.app.models import ReplacementSecurity as HarvestReplacementSecurity
from harvest_alert.app.models import TaxAssumptions as HarvestTaxAssumptions
from harvest_alert.app.models import TaxLot as HarvestTaxLot
from harvest_alert.app.models import Transaction as HarvestTransaction
from harvest_alert.app.providers.brokerage_provider import LocalBrokerageProvider
from harvest_alert.app.services.analyzer import HarvestAlertAnalyzer
from harvest_alert.app.services.reporting import build_markdown_report as build_harvest_markdown_report
from harvest_alert.app.services.visualization import (
    plot_losses as plot_harvest_losses,
    plot_similarity as plot_harvest_similarity,
    plot_tax_savings as plot_harvest_tax_savings,
)
from moat_watch.app.config import DEFAULT_QUARTER as DEFAULT_MOAT_QUARTER
from moat_watch.app.config import WATCHLIST_FILE as DEFAULT_MOAT_WATCHLIST_FILE
from moat_watch.app.models import WatchlistItem as MoatWatchItem
from moat_watch.app.providers.moat_provider import LocalMoatProvider
from moat_watch.app.services.analyzer import MoatWatchAnalyzer
from moat_watch.app.services.reporting import build_markdown_report as build_moatwatch_markdown_report
from moat_watch.app.services.visualization import (
    plot_moat_score_history as plot_moatwatch_score_history,
    plot_peer_comparison as plot_moatwatch_peer_comparison,
    plot_signal_radar as plot_moatwatch_signal_radar,
)
from value_check.app.config import DEFAULT_SAMPLE_TICKERS as DEFAULT_VALUECHECK_SAMPLE_TICKERS
from value_check.app.providers.valuation_provider import LocalValuationProvider
from value_check.app.services.analyzer import ValueCheckAnalyzer
from value_check.app.services.reporting import build_markdown_report as build_valuecheck_markdown_report
from value_check.app.services.visualization import (
    plot_peer_comparison as plot_valuecheck_peer_comparison,
    plot_percentile_bars as plot_valuecheck_percentile_bars,
    plot_scorecard as plot_valuecheck_scorecard,
)


st.set_page_config(page_title="ETF Analytics Platform", layout="wide")
CACHE_CATALOG_PATH = Path("data/catalog/us_etf_catalog.csv")


def _inject_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(255, 209, 102, 0.18), transparent 30%),
                radial-gradient(circle at top right, rgba(17, 138, 178, 0.15), transparent 28%),
                linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
        }
        .hero-card {
            background: linear-gradient(135deg, #0f172a 0%, #1d3557 45%, #22577a 100%);
            border-radius: 24px;
            padding: 1.5rem 1.75rem;
            color: white;
            box-shadow: 0 20px 50px rgba(15, 23, 42, 0.18);
            margin-bottom: 1rem;
        }
        .hero-eyebrow {
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-size: 0.75rem;
            opacity: 0.8;
            margin-bottom: 0.35rem;
        }
        .hero-title {
            font-size: 2rem;
            line-height: 1.1;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }
        .hero-copy {
            font-size: 1rem;
            max-width: 56rem;
            opacity: 0.92;
        }
        .summary-card {
            background: white;
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.06);
            min-height: 135px;
        }
        .summary-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748b;
            margin-bottom: 0.4rem;
        }
        .summary-value {
            font-size: 1.45rem;
            line-height: 1.1;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 0.45rem;
        }
        .summary-copy {
            font-size: 0.92rem;
            color: #334155;
        }
        .viral-card {
            background: linear-gradient(135deg, #fef3c7 0%, #fff7ed 50%, #e0f2fe 100%);
            border: 1px solid rgba(249, 115, 22, 0.15);
            border-radius: 24px;
            padding: 1.2rem 1.35rem;
            box-shadow: 0 14px 34px rgba(249, 115, 22, 0.10);
            margin-bottom: 1rem;
        }
        .viral-kicker {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #9a3412;
            margin-bottom: 0.35rem;
        }
        .viral-title {
            font-size: 1.55rem;
            line-height: 1.15;
            font-weight: 800;
            color: #7c2d12;
            margin-bottom: 0.45rem;
        }
        .viral-copy {
            font-size: 0.98rem;
            color: #7c2d12;
        }
        .section-kicker {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748b;
            margin-bottom: 0.3rem;
        }
        .risk-card {
            background: linear-gradient(180deg, #fff 0%, #f8fafc 100%);
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-left: 6px solid #ef4444;
            border-radius: 18px;
            padding: 0.95rem 1rem;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
            min-height: 170px;
        }
        .risk-rank {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #b91c1c;
            margin-bottom: 0.35rem;
        }
        .risk-title {
            font-size: 1.05rem;
            line-height: 1.2;
            font-weight: 800;
            color: #111827;
            margin-bottom: 0.35rem;
        }
        .risk-metric {
            font-size: 0.92rem;
            color: #374151;
            margin-bottom: 0.25rem;
        }
        .risk-copy {
            font-size: 0.88rem;
            color: #4b5563;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _parse_portfolio(raw_text: str) -> list[dict[str, Any]]:
    payload = json.loads(raw_text)
    if isinstance(payload, dict) and "positions" in payload:
        payload = payload["positions"]
    if not isinstance(payload, list):
        raise ValueError("Portfolio input must be a JSON array of positions.")
    return payload


def _show_warnings(warnings: list[str]) -> None:
    if not warnings:
        st.success("No major warnings triggered for this portfolio.")
        return
    for warning in warnings:
        st.warning(warning)


def _show_recommendations(recommendations: list[str]) -> None:
    if not recommendations:
        return
    st.subheader("Recommendations")
    for recommendation in recommendations:
        st.write(f"- {recommendation}")


def _show_supported_caption(supported_tickers: list[str], catalog_count: int) -> None:
    st.caption(f"Supported ETFs: {', '.join(supported_tickers)}")
    if catalog_count:
        st.caption(
            f"Cached ETF catalog loaded: {catalog_count} U.S.-listed ETF symbols. "
            "The quick picker shows analysis-ready ETFs with local holdings data."
        )
    else:
        st.info("No cached ETF catalog found yet. Run `python fetch_etf_catalog.py` to cache the ETF universe locally.")


def _render_hero() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-eyebrow">ETF Analytics Platform</div>
            <div class="hero-title">Look through the labels. See what your portfolio really depends on.</div>
            <div class="hero-copy">
                Move from ETF allocations to hidden overlap, true global exposure, and the macro engines actually driving your risk.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _portfolio_upload_widget(state_key_prefix: str) -> Optional[str]:
    uploaded_file = st.file_uploader(
        "Upload portfolio JSON",
        type=["json"],
        key=f"{state_key_prefix}_upload",
        help="Upload a JSON array like [{\"ticker\": \"VTI\", \"amount\": 2000}]",
    )
    if uploaded_file is None:
        return None
    return uploaded_file.getvalue().decode("utf-8")


def _json_upload_widget(label: str, state_key_prefix: str, help_text: str) -> Optional[str]:
    uploaded_file = st.file_uploader(
        label,
        type=["json"],
        key=f"{state_key_prefix}_upload",
        help=help_text,
    )
    if uploaded_file is None:
        return None
    return uploaded_file.getvalue().decode("utf-8")


def _portfolio_picker(
    *,
    title: str,
    supported_tickers: list[str],
    catalog_df: pd.DataFrame,
    state_key_prefix: str,
    default_tickers: list[str],
    default_total_amount: float = 10000.0,
    default_amounts: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    st.markdown(f"**{title}**")
    name_map = {
        str(row["ticker"]).upper(): str(row["security_name"])
        for _, row in catalog_df.iterrows()
    }
    selected = st.multiselect(
        "Pick ETFs",
        options=supported_tickers,
        default=[ticker for ticker in default_tickers if ticker in supported_tickers],
        key=f"{state_key_prefix}_tickers",
    )
    if not selected:
        st.caption("Pick one or more ETFs to build an allocation.")
        return []

    total_amount = st.number_input(
        "Total portfolio amount",
        min_value=0.0,
        value=float(default_total_amount),
        step=500.0,
        key=f"{state_key_prefix}_total_amount",
        help="Enter the total amount you want to allocate across the selected ETFs.",
    )
    st.caption("Drag each ETF slider left or right to lower or raise its share of the total portfolio.")

    default_amounts = default_amounts or {}
    default_amount_total = sum(
        float(amount)
        for ticker, amount in default_amounts.items()
        if ticker in selected and float(amount) > 0
    )

    raw_weights: dict[str, float] = {}
    for ticker in selected:
        display_name = name_map.get(ticker, ticker)
        default_slider_value = 50
        if default_amount_total > 0 and ticker in default_amounts:
            default_slider_value = max(
                1,
                min(100, int(round((float(default_amounts[ticker]) / default_amount_total) * 100))),
            )
        raw_weights[ticker] = float(
            st.slider(
                f"{ticker} allocation tilt",
                min_value=0,
                max_value=100,
                value=default_slider_value,
                step=1,
                key=f"{state_key_prefix}_{ticker}_tilt",
                help=f"{display_name}. Left = smaller weight, right = larger weight.",
            )
        )

    total_weight = sum(raw_weights.values())
    if total_weight <= 0:
        equal_weight = 1.0 / len(selected)
        normalized_weights = {ticker: equal_weight for ticker in selected}
    else:
        normalized_weights = {ticker: raw_weights[ticker] / total_weight for ticker in selected}

    portfolio: list[dict[str, Any]] = []
    preview_rows: list[dict[str, Any]] = []
    for ticker in selected:
        allocation_pct = normalized_weights[ticker]
        amount = float(total_amount) * allocation_pct
        portfolio.append({"ticker": ticker, "amount": round(amount, 2)})
        preview_rows.append(
            {
                "ticker": ticker,
                "allocation_pct": round(allocation_pct * 100, 2),
                "amount": round(amount, 2),
            }
        )
    st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True)
    return portfolio


def _render_dependency_summary_cards(summary: dict[str, Any], scores: dict[str, Any]) -> None:
    cards = [
        ("Top Hidden Dependency", summary.get("top_hidden_dependency") or "N/A", "The macro engine with the biggest invisible grip on the portfolio."),
        ("Reality Gap", f"{scores['economic_reality_gap']:.1f}/100", "How misleading the ETF labels are versus the actual economic concentration underneath."),
        ("Diversification", f"{scores['global_diversification_score']:.1f}/100", "A concentration-aware score that rewards broader country, revenue, and driver spread."),
        ("Macro Dependence", f"{scores['macro_dependence_score']:.1f}/100", "Higher means the portfolio is tied to fewer economic engines than it first appears."),
    ]
    columns = st.columns(4)
    for column, (label, value, copy) in zip(columns, cards):
        column.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">{label}</div>
                <div class="summary-value">{value}</div>
                <div class="summary-copy">{copy}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_viral_summary_card(summary: dict[str, Any]) -> None:
    headline = summary.get("top_hidden_dependency") or "Hidden dependency"
    top_country = summary.get("top_country") or "N/A"
    top_region = summary.get("top_region") or "N/A"
    gap = summary.get("economic_reality_gap", 0.0)
    diversification = summary.get("global_diversification_score", 0.0)
    warning = summary.get("top_warning") or "No major warning triggered."
    st.markdown(
        f"""
        <div class="viral-card">
            <div class="viral-kicker">Screenshot-Worthy Summary</div>
            <div class="viral-title">Your portfolio quietly depends most on {headline}.</div>
            <div class="viral-copy">
                Top country: <strong>{top_country}</strong>. Top region: <strong>{top_region}</strong>.
                Economic Reality Gap: <strong>{gap:.1f}/100</strong>. Diversification Score: <strong>{diversification:.1f}/100</strong>.
                <br><br>
                {warning}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_hf_summary_cards(summary: dict[str, Any], scores: dict[str, Any]) -> None:
    top_dependency = summary.get("top_dependency", {})
    top_country = summary.get("top_country", {})
    top_region = summary.get("top_region", {})
    cards = [
        (
            "Top Hidden Dependency",
            top_dependency.get("display_name", "N/A"),
            "The dominant macro engine driving hidden portfolio dependence.",
        ),
        (
            "Reality Gap",
            f"{scores['economic_reality_gap']:.1f}/100",
            "How much the ETF mix understates company, country, and dependency concentration.",
        ),
        (
            "Diversification",
            f"{scores['global_diversification_score']:.1f}/100",
            "Rewards broader country, revenue, dependency, and currency spread.",
        ),
        (
            "Macro Dependence",
            f"{scores['macro_dependence_score']:.1f}/100",
            "Higher means the portfolio is overly tied to a small set of economic drivers.",
        ),
    ]
    columns = st.columns(4)
    for column, (label, value, copy) in zip(columns, cards):
        column.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">{label}</div>
                <div class="summary-value">{value}</div>
                <div class="summary-copy">{copy}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    kicker_col1, kicker_col2 = st.columns(2)
    kicker_col1.caption(
        f"Top country: {top_country.get('name', 'N/A')} ({float(top_country.get('exposure_pct', 0.0)):.1f}%)"
    )
    kicker_col2.caption(
        f"Top region: {top_region.get('name', 'N/A')} ({float(top_region.get('exposure_pct', 0.0)):.1f}%)"
    )


def _render_hf_viral_summary_card(summary: dict[str, Any]) -> None:
    top_dependency = summary.get("top_dependency", {})
    top_country = summary.get("top_country", {})
    top_region = summary.get("top_region", {})
    warning = summary.get("top_warning") or "No major warning triggered."
    st.markdown(
        f"""
        <div class="viral-card">
            <div class="viral-kicker">Flagship Dependency Readout</div>
            <div class="viral-title">Your portfolio quietly depends most on {top_dependency.get("display_name", "hidden macro drivers")}.</div>
            <div class="viral-copy">
                Top country: <strong>{top_country.get("name", "N/A")}</strong>. Top region: <strong>{top_region.get("name", "N/A")}</strong>.
                Economic Reality Gap: <strong>{float(summary.get("economic_reality_gap", 0.0)):.1f}/100</strong>.
                Diversification Score: <strong>{float(summary.get("global_diversification_score", 0.0)):.1f}/100</strong>.
                <br><br>
                {warning}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_earnings_viral_card(result: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="viral-card">
            <div class="viral-kicker">EarningsClarity</div>
            <div class="viral-title">{result['ticker']} {result['quarter']}: {result['headline_result']['headline_classification'].title()} headline, {result['tone_shift']['tone_shift_label'].replace('_', ' ')} tone.</div>
            <div class="viral-copy">
                Thesis status: <strong>{result['thesis_status']}</strong>. Confidence: <strong>{float(result['confidence_score']):.2f}</strong>.
                <br><br>
                {result['long_term_takeaway']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_earnings_summary_cards(result: dict[str, Any]) -> None:
    headline = result["headline_result"]
    tone = result["tone_shift"]
    guidance = result["guidance_view"]
    cards = [
        (
            "Headline",
            str(headline["headline_classification"]).title(),
            f"Revenue {headline['revenue_classification']}, EPS {headline['eps_classification']}.",
        ),
        (
            "Tone Shift",
            str(tone["tone_shift_label"]).replace("_", " ").title(),
            f"Shift score: {float(tone['tone_shift_score']):.1f}",
        ),
        (
            "Guidance View",
            str(guidance["guidance_label"]).title(),
            f"Caution {float(guidance['guidance_caution_score']):.1f} vs positive {float(guidance['guidance_positive_score']):.1f}.",
        ),
        (
            "Thesis Status",
            str(result["thesis_status"]).title(),
            "Long-term-holder interpretation after weighting headline, tone, and guidance.",
        ),
    ]
    columns = st.columns(4)
    for column, (label, value, copy) in zip(columns, cards):
        column.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">{label}</div>
                <div class="summary-value">{value}</div>
                <div class="summary-copy">{copy}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_cost_viral_card(summary: dict[str, Any]) -> None:
    biggest_category = str(summary.get("biggest_cost_category", "hidden frictions")).replace("_", " ")
    st.markdown(
        f"""
        <div class="viral-card">
            <div class="viral-kicker">True Cost of Investing</div>
            <div class="viral-title">You are not just paying a small annual fee. This portfolio may forfeit about ${float(summary.get("total_30_year_dollars_lost", 0.0)):,.0f} of ending wealth.</div>
            <div class="viral-copy">
                Hidden annual drag: <strong>{float(summary.get("total_hidden_annual_drag_rate", 0.0)):.2%}</strong>.
                Biggest cost bucket: <strong>{biggest_category}</strong>.
                Gross ending value: <strong>${float(summary.get("gross_ending_value", 0.0)):,.0f}</strong>.
                Net ending value: <strong>${float(summary.get("net_ending_value", 0.0)):,.0f}</strong>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_cost_summary_cards(result: dict[str, Any]) -> None:
    summary = result["summary"]
    blended = result["blended_cost_metrics"]
    cards = [
        (
            "Annual Hidden Drag",
            f"{float(summary['total_hidden_annual_drag_rate']):.2%}",
            "The all-in modeled friction rate after fees, taxes, spreads, and cash drag.",
        ),
        (
            "30-Year Wealth Lost",
            f"${float(summary['total_30_year_dollars_lost']):,.0f}",
            "The modeled ending-value gap between gross compounding and net compounding.",
        ),
        (
            "Blended Expense Ratio",
            f"{float(blended['blended_expense_ratio']):.2%}",
            "Visible fund fees often matter less than the full stack of hidden frictions.",
        ),
        (
            "Biggest Cost",
            str(summary["biggest_cost_category"]).replace("_", " ").title(),
            "The friction source currently doing the most long-term damage in the model.",
        ),
    ]
    columns = st.columns(4)
    for column, (label, value, copy) in zip(columns, cards):
        column.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">{label}</div>
                <div class="summary-value">{value}</div>
                <div class="summary-copy">{copy}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_regime_viral_card(result: dict[str, Any]) -> None:
    summary = result["plain_english_summary"]
    top_analog = "No historical analog available"
    if result["historical_analogs"]:
        top_analog = (
            f"{result['historical_analogs'][0]['observation_date']} "
            f"({result['historical_analogs'][0]['regime_label']})"
        )
    st.markdown(
        f"""
        <div class="viral-card">
            <div class="viral-kicker">Economic Regime Translator</div>
            <div class="viral-title">Current regime: {result['regime_label']}.</div>
            <div class="viral-copy">
                Confidence: <strong>{float(result['confidence_score']):.0f}/100</strong>.
                Top historical analog: <strong>{top_analog}</strong>.
                <br><br>
                {summary['summary_paragraph']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_regime_summary_cards(result: dict[str, Any]) -> None:
    top_driver = result["primary_drivers"][0] if result["primary_drivers"] else "Mixed signals"
    top_analog = result["historical_analogs"][0]["observation_date"] if result["historical_analogs"] else "N/A"
    cards = [
        (
            "Regime",
            result["regime_label"],
            "The current macro label produced by the rule-based regime classifier.",
        ),
        (
            "Confidence",
            f"{float(result['confidence_score']):.0f}/100",
            "Higher means more of the macro signals are pointing in the same direction.",
        ),
        (
            "Top Driver",
            top_driver,
            "The main signal currently shaping the regime classification.",
        ),
        (
            "Top Historical Analog",
            top_analog,
            "The closest historical period in the bundled sample regime history.",
        ),
    ]
    columns = st.columns(4)
    for column, (label, value, copy) in zip(columns, cards):
        column.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">{label}</div>
                <div class="summary-value">{value}</div>
                <div class="summary-copy">{copy}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_valuecheck_viral_card(result: dict[str, Any]) -> None:
    pe_row = next((row for row in result["historical_comparison"] if row["metric"] == "pe_ratio"), None)
    peer_row = next((row for row in result["peer_comparison"] if row["metric"] == "pe_ratio"), None)
    pe_copy = "P/E history not available"
    if pe_row and pe_row["current_value"] is not None:
        pe_copy = (
            f"P/E {float(pe_row['current_value']):.1f}x vs history percentile "
            f"{float(pe_row['percentile_rank'] or 0.0):.0f}"
        )
    peer_copy = "Peer P/E context limited"
    if peer_row and peer_row["peer_median"] is not None:
        peer_copy = f"peer median {float(peer_row['peer_median']):.1f}x"
    st.markdown(
        f"""
        <div class="viral-card">
            <div class="viral-kicker">ValueCheck</div>
            <div class="viral-title">{result['ticker']} looks {result['verdict']['label'].replace('_', ' ')} on this blended valuation view.</div>
            <div class="viral-copy">
                {pe_copy}; {peer_copy}. Confidence: <strong>{float(result['confidence_score']):.0f}/100</strong>.
                <br><br>
                {result['long_term_takeaway']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_valuecheck_summary_cards(result: dict[str, Any]) -> None:
    metrics = result["current_metrics"]
    spread = result["treasury_context"]["fcf_spread"]
    cards = [
        (
            "Verdict",
            result["verdict"]["label"].replace("_", " ").title(),
            "Composite call across own-history percentiles, peer premiums, and cash-flow context.",
        ),
        (
            "Composite Score",
            f"{float(result['composite_score']):.1f}/100",
            "Higher scores mean richer valuation context across the available metrics.",
        ),
        (
            "FCF vs Treasury",
            "N/A" if spread is None else f"{float(spread):+.2%}",
            "Free-cash-flow yield minus Treasury yield. A more negative spread usually means richer expectations.",
        ),
        (
            "Current P/E",
            "N/A" if metrics.get("pe_ratio") is None else f"{float(metrics['pe_ratio']):.1f}x",
            "Trailing earnings multiple when earnings are positive and meaningful.",
        ),
    ]
    columns = st.columns(4)
    for column, (label, value, copy) in zip(columns, cards):
        column.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">{label}</div>
                <div class="summary-value">{value}</div>
                <div class="summary-copy">{copy}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_moatwatch_viral_card(result: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="viral-card">
            <div class="viral-kicker">MoatWatch</div>
            <div class="viral-title">{result['ticker']} moat health is {result['moat_health_label']}.</div>
            <div class="viral-copy">
                Score: <strong>{float(result['moat_health_score']):.1f}/100</strong>.
                QoQ change: <strong>{'N/A' if result['score_change_qoq'] is None else f"{float(result['score_change_qoq']):+.1f}"}</strong>.
                Transition: <strong>{str(result['transition_label']).replace('_', ' ')}</strong>.
                <br><br>
                {result['long_term_takeaway']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_moatwatch_summary_cards(result: dict[str, Any]) -> None:
    cards = [
        (
            "Moat Health",
            result["moat_health_label"],
            "Color-coded moat status based on operating, reinvestment, and commentary signals.",
        ),
        (
            "Moat Score",
            f"{float(result['moat_health_score']):.1f}/100",
            "Higher means the company still looks to be defending or extending its edge.",
        ),
        (
            "QoQ Change",
            "N/A" if result["score_change_qoq"] is None else f"{float(result['score_change_qoq']):+.1f}",
            "Change versus the prior quarter.",
        ),
        (
            "YoY Change",
            "N/A" if result["score_change_yoy"] is None else f"{float(result['score_change_yoy']):+.1f}",
            "Change versus the same quarter last year.",
        ),
    ]
    columns = st.columns(4)
    for column, (label, value, copy) in zip(columns, cards):
        column.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">{label}</div>
                <div class="summary-value">{value}</div>
                <div class="summary-copy">{copy}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_harvest_viral_card(result: dict[str, Any]) -> None:
    top = result["plain_english_summary"].get("top_opportunity")
    if not top:
        st.markdown(
            """
            <div class="viral-card">
                <div class="viral-kicker">HarvestAlert</div>
                <div class="viral-title">No worthwhile tax-loss harvesting alert is currently clearing your thresholds.</div>
                <div class="viral-copy">
                    The supplied taxable positions either are not at losses, are too small to matter after friction, or do not have a clean replacement candidate.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    replacement = top.get("recommended_replacement") or {}
    st.markdown(
        f"""
        <div class="viral-card">
            <div class="viral-kicker">HarvestAlert</div>
            <div class="viral-title">{top['ticker']} is the top harvest opportunity right now.</div>
            <div class="viral-copy">
                Estimated tax savings: <strong>${float(top['estimated_tax_savings']):,.0f}</strong>.
                Net benefit after trading friction: <strong>${float(top['net_estimated_benefit']):,.0f}</strong>.
                Replacement: <strong>{replacement.get('ticker', 'No clean replacement')}</strong>.
                Wash-sale risk: <strong>{str(top['wash_sale_risk_level']).title()}</strong>.
                <br><br>
                {top['alert_text']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_harvest_summary_cards(result: dict[str, Any]) -> None:
    cards = [
        (
            "Total Tax Savings",
            f"${float(result['estimated_total_tax_savings']):,.0f}",
            "Estimated gross tax value across the ranked harvest candidates.",
        ),
        (
            "Net Benefit",
            f"${float(result['estimated_total_net_benefit']):,.0f}",
            "Estimated tax value after modeled trading friction.",
        ),
        (
            "Opportunities",
            str(len(result["opportunities"])),
            "Harvest candidates that cleared the configured thresholds.",
        ),
        (
            "High-Risk Cases",
            str(sum(1 for row in result["opportunities"] if row["wash_sale_risk_level"] == "high")),
            "Candidates that still look interesting economically but need extra wash-sale caution.",
        ),
    ]
    columns = st.columns(4)
    for column, (label, value, copy) in zip(columns, cards):
        column.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">{label}</div>
                <div class="summary-value">{value}</div>
                <div class="summary-copy">{copy}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_globalgap_viral_card(result: dict[str, Any]) -> None:
    recommendation = result["recommendation"]
    valuation = result["valuation_gap"]
    dollar = result["dollar_cycle"]
    st.markdown(
        f"""
        <div class="viral-card">
            <div class="viral-kicker">GlobalGap</div>
            <div class="viral-title">{recommendation['headline']}</div>
            <div class="viral-copy">
                International equities trade at a <strong>{float(valuation['international_discount_pct']):.1f}% discount</strong>
                to US equities, while the dollar is in a <strong>{str(dollar['regime']).replace('_', ' ').title()}</strong> regime.
                <br><br>
                {recommendation['plain_english_note']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_globalgap_summary_cards(result: dict[str, Any]) -> None:
    exposure = result["portfolio_exposure"]
    valuation = result["valuation_gap"]
    analogs = result["historical_analogs"]
    simulation = result["simulation"]
    cards = [
        (
            "US Weight",
            f"{float(exposure['portfolio_us_weight']) * 100:.0f}%",
            exposure["home_bias_level"],
        ),
        (
            "Intl Discount",
            f"{float(valuation['international_discount_pct']):.1f}%",
            "Current discount of international equities versus US forward P/E.",
        ),
        (
            "Analog Outcome",
            f"{float(analogs['average_following_5y_outperformance_pct']):.1f}%",
            "Average annualized international outperformance after similar spreads.",
        ),
        (
            "Sharpe Change",
            f"{float(simulation['sharpe_ratio_change']):+.2f}",
            "Historical change in risk-adjusted return for the diversified mix.",
        ),
    ]
    columns = st.columns(4)
    for column, (label, value, copy) in zip(columns, cards):
        column.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">{label}</div>
                <div class="summary-value">{value}</div>
                <div class="summary-copy">{copy}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _figure_download_button(label: str, figure: go.Figure, file_name: str, key: str) -> None:
    html = figure.to_html(include_plotlyjs="cdn", full_html=True)
    st.download_button(
        label=label,
        data=html,
        file_name=file_name,
        mime="text/html",
        key=key,
    )


def _result_download_buttons(result: dict[str, Any], figure_map: dict[str, go.Figure], key_prefix: str) -> None:
    st.download_button(
        "Download analysis JSON",
        data=json.dumps(result, indent=2),
        file_name=f"{key_prefix}_analysis.json",
        mime="application/json",
        key=f"{key_prefix}_result_json",
    )
    for chart_name, figure in figure_map.items():
        _figure_download_button(
            label=f"Download {chart_name}",
            figure=figure,
            file_name=f"{key_prefix}_{chart_name}.html",
            key=f"{key_prefix}_{chart_name}",
        )


def _fetch_live_news_bundle(news_provider: GoogleNewsRSSProvider, event_templates: list[Any]) -> dict[str, Any]:
    headlines = news_provider.fetch_headlines(limit=12)
    suggestions = suggest_dynamic_events_from_headlines(headlines, event_templates)
    return {
        "headlines": [headline.to_dict() for headline in headlines],
        "headline_context": headlines_to_context(headlines),
        "suggestions": suggestions,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def _render_live_risk_cards(suggestions: list[dict[str, Any]]) -> None:
    if not suggestions:
        st.info("No live risk suggestions were inferred from the latest headlines.")
        return
    columns = st.columns(min(5, len(suggestions)))
    for index, (column, suggestion) in enumerate(zip(columns, suggestions), start=1):
        matched_headline = ""
        if suggestion.get("matched_headlines"):
            matched_headline = suggestion["matched_headlines"][0]["title"]
        column.markdown(
            f"""
            <div class="risk-card">
                <div class="risk-rank">Live Risk #{index}</div>
                <div class="risk-title">{suggestion['display_name']}</div>
                <div class="risk-metric">Confidence: <strong>{float(suggestion['confidence_score']):.0f}/100</strong></div>
                <div class="risk-metric">Severity: <strong>{float(suggestion['suggested_severity']):.1f}x</strong></div>
                <div class="risk-metric">Headline hits: <strong>{int(suggestion['matched_headline_count'])}</strong></div>
                <div class="risk-copy">{matched_headline}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _schedule_autorefresh(interval_seconds: int) -> None:
    components.html(
        f"""
        <script>
        setTimeout(function() {{
            window.parent.location.reload();
        }}, {int(interval_seconds) * 1000});
        </script>
        """,
        height=0,
        width=0,
    )


def _news_bundle_is_stale(bundle: dict[str, Any] | None, interval_seconds: int) -> bool:
    if not bundle or not bundle.get("fetched_at"):
        return True
    try:
        fetched_at = datetime.fromisoformat(str(bundle["fetched_at"]))
    except ValueError:
        return True
    if fetched_at.tzinfo is None:
        fetched_at = fetched_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - fetched_at >= timedelta(seconds=interval_seconds)


_inject_theme()
st.title("ETF Analytics Platform")
st.caption("Look through ETF labels to see overlap, concentration, true global exposure, and hidden macro dependency.")
_render_hero()

overlap_supported = LiveHybridHoldingsProvider(DEFAULT_DATA_DIR).supported_etfs()
global_supported = GlobalCSVHoldingsProvider(ETF_HOLDINGS_DIR).supported_etfs()
dependency_analyzer = EconomicDependencyAnalyzer(CSVDependencyDataProvider(DEPENDENCY_HOLDINGS_DIR))
dependency_supported = dependency_analyzer.data_provider.supported_etfs()
dependency_scenarios = dependency_analyzer.data_provider.get_scenarios()
hf_analyzer = HedgefundDependencyAnalyzer(CSVEngineDataProvider(HF_HOLDINGS_DIR))
hf_supported = hf_analyzer.data_provider.supported_etfs()
hf_scenarios = hf_analyzer.data_provider.get_scenarios()
hf_event_templates = hf_analyzer.data_provider.get_event_templates()
hf_news_provider = GoogleNewsRSSProvider()
earnings_analyzer = EarningsClarityAnalyzer()
earnings_event_provider = LocalEarningsEventProvider()
earnings_events = earnings_event_provider.list_events()
earnings_companies = sorted({event.ticker for event in earnings_events})
earnings_quarters = sorted({event.quarter for event in earnings_events}, reverse=True)
true_cost_analyzer = TrueCostAnalyzer()
regime_analyzer = EconomicRegimeAnalyzer()
harvest_provider = LocalBrokerageProvider()
harvest_analyzer = HarvestAlertAnalyzer(harvest_provider)
moatwatch_analyzer = MoatWatchAnalyzer()
moatwatch_provider = LocalMoatProvider()
moatwatch_supported = moatwatch_provider.supported_tickers()
globalgap_analyzer = GlobalGapAnalyzer()
valuecheck_analyzer = ValueCheckAnalyzer()
valuecheck_provider = LocalValuationProvider()
valuecheck_supported = valuecheck_provider.supported_tickers()
regime_history_df = pd.read_csv(DEFAULT_REGIME_HISTORY_FILE)
cost_portfolio_samples = {
    "High-fee mixed portfolio": DEFAULT_COST_PORTFOLIO_FILE,
    "Low-cost index portfolio": DEFAULT_COST_ALTERNATIVE_PORTFOLIO_FILE,
}
cost_assumption_samples = {
    "Taxable account": DEFAULT_COST_ASSUMPTIONS_FILE,
    "Roth IRA": Path("true_cost_of_investing/app/data/assumptions/roth_ira.json"),
    "Advisory fee scenario": Path("true_cost_of_investing/app/data/assumptions/advisory_fee_scenario.json"),
    "High-turnover scenario": Path("true_cost_of_investing/app/data/assumptions/high_turnover_scenario.json"),
}
catalog_df = load_etf_catalog(CACHE_CATALOG_PATH)
catalog_count = len(catalog_df.index)

with st.sidebar:
    st.subheader("Workspace")
    st.write("Use the quick picker, upload JSON, or paste portfolio JSON manually.")
    st.write(f"Catalog ETFs cached: {catalog_count}")
    st.write(
        f"Analysis-ready ETFs: {len(sorted(set(overlap_supported) | set(global_supported) | set(dependency_supported) | set(hf_supported)))}"
    )
    st.write("Best for screenshots: run the dependency or investing-cost tabs after selecting a sample portfolio.")

overlap_tab, global_tab, dependency_tab, hf_tab, earnings_tab, cost_tab, regime_tab, globalgap_tab, valuecheck_tab, moatwatch_tab, harvest_tab = st.tabs(
    [
        "Overlap Detector",
        "Global Exposure Map",
        "Economic Dependency Heatmap",
        "Hedgefund Dependency Engine",
        "EarningsClarity",
        "True Cost of Investing",
        "Economic Regime Translator",
        "GlobalGap",
        "ValueCheck",
        "MoatWatch",
        "HarvestAlert",
    ]
)

with overlap_tab:
    st.subheader("ETF Hidden Overlap & Concentration Detector")
    _show_supported_caption(overlap_supported, catalog_count)
    overlap_include_all = st.toggle(
        "Auto-include all supported overlap ETFs",
        value=True,
        key="overlap_include_all_supported",
        help="When enabled, the quick picker starts with every locally supported overlap ETF selected instead of the smaller sample set.",
    )
    st.caption(
        "Quick Picker only shows ETFs that are analyzable right now through local holdings, live support, or approved proxy coverage like SPY/IVV/SPLG/SCHX -> VOO, ITOT/SCHB -> VTI, VEU/ACWX -> IXUS, IEMG/VWO -> EEM, ONEQ/QQQM -> QQQ, and VEA/IEFA/EFA/SCHF -> SPDW."
    )
    overlap_defaults = sorted(overlap_supported) if overlap_include_all else [item["ticker"] for item in DEFAULT_SAMPLE_PORTFOLIO]
    overlap_total_default = float(len(overlap_defaults) * 1000) if overlap_include_all else float(sum(item["amount"] for item in DEFAULT_SAMPLE_PORTFOLIO))
    overlap_seed_portfolio = (
        [{"ticker": ticker, "amount": 1000.0} for ticker in overlap_defaults]
        if overlap_include_all
        else DEFAULT_SAMPLE_PORTFOLIO
    )
    picked_overlap_portfolio = _portfolio_picker(
        title="Quick Picker",
        supported_tickers=overlap_supported,
        catalog_df=catalog_df,
        state_key_prefix="overlap_picker",
        default_tickers=overlap_defaults,
        default_total_amount=overlap_total_default,
        default_amounts={item["ticker"]: float(item["amount"]) for item in overlap_seed_portfolio},
    )
    overlap_default_portfolio = picked_overlap_portfolio or DEFAULT_SAMPLE_PORTFOLIO
    overlap_default = json.dumps(overlap_default_portfolio, indent=2)
    with st.form("overlap_form"):
        overlap_input = st.text_area(
            "Portfolio JSON",
            value=overlap_default,
            height=220,
        )
        overlap_submit = st.form_submit_button("Analyze Overlap")

    if overlap_submit:
        try:
            overlap_portfolio = _parse_portfolio(overlap_input)
            overlap_result = PortfolioAnalyzer().analyze(overlap_portfolio).to_dict()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unable to analyze overlap portfolio: {exc}")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Diversification Score", f"{overlap_result['diversification_score']:.1f}")
            col2.metric("Hidden Concentration", f"{overlap_result['hidden_concentration_score']:.1f}")
            col3.metric("Redundancy Index", f"{overlap_result['redundancy_index']:.1f}")

            _show_warnings(overlap_result["warnings"])

            st.plotly_chart(plot_top_holdings_bar(overlap_result), use_container_width=True)
            st.plotly_chart(plot_sector_exposure_chart(overlap_result), use_container_width=True)
            st.plotly_chart(plot_overlap_heatmap(overlap_result), use_container_width=True)

            st.subheader("Top Underlying Exposures")
            st.dataframe(pd.DataFrame(overlap_result["underlying_exposures"]).head(15), use_container_width=True)

            st.subheader("Overlap Pairs")
            st.dataframe(pd.DataFrame(overlap_result["overlap_pairs"]), use_container_width=True)

            _show_recommendations(overlap_result["optimization_suggestions"])

with global_tab:
    st.subheader("Global ETF Exposure Map")
    _show_supported_caption(global_supported, catalog_count)
    global_include_all = st.toggle(
        "Auto-include all supported global ETFs",
        value=True,
        key="global_include_all_supported",
        help="When enabled, the quick picker starts with every analyzable Global Exposure ETF selected.",
    )
    st.caption(
        "Quick Picker shows the same practical ETF universe as overlap, including approved proxy coverage like SPY/IVV/SPLG/SCHX -> VOO, ITOT/SCHB -> VTI, VEU/ACWX/VEA/IEFA/EFA/SCHF -> IXUS, IEMG/VWO -> EEM, and ONEQ/QQQM -> QQQ."
    )
    global_defaults = sorted(global_supported) if global_include_all else [item["ticker"] for item in DEFAULT_GLOBAL_SAMPLE_PORTFOLIO]
    global_total_default = float(len(global_defaults) * 1000) if global_include_all else float(sum(item["amount"] for item in DEFAULT_GLOBAL_SAMPLE_PORTFOLIO))
    global_seed_portfolio = (
        [{"ticker": ticker, "amount": 1000.0} for ticker in global_defaults]
        if global_include_all
        else DEFAULT_GLOBAL_SAMPLE_PORTFOLIO
    )
    picked_global_portfolio = _portfolio_picker(
        title="Quick Picker",
        supported_tickers=global_supported,
        catalog_df=catalog_df,
        state_key_prefix="global_picker",
        default_tickers=global_defaults,
        default_total_amount=global_total_default,
        default_amounts={item["ticker"]: float(item["amount"]) for item in global_seed_portfolio},
    )
    global_default_portfolio = picked_global_portfolio or DEFAULT_GLOBAL_SAMPLE_PORTFOLIO
    global_default = json.dumps(global_default_portfolio, indent=2)
    with st.form("global_form"):
        global_input = st.text_area(
            "Portfolio JSON",
            value=global_default,
            height=220,
        )
        global_submit = st.form_submit_button("Analyze Global Exposure")

    if global_submit:
        try:
            global_portfolio = _parse_portfolio(global_input)
            global_result = GlobalExposureAnalyzer().analyze(global_portfolio).to_dict()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unable to analyze global portfolio: {exc}")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Global Dependence Score", f"{global_result['global_dependence_score']:.1f}")
            col2.metric("Economic Reality Gap", f"{global_result['economic_reality_gap']:.1f}")
            col3.metric("Effective Countries", f"{global_result['dashboard_summary']['effective_countries']:.2f}")

            _show_warnings(global_result["warnings"])

            st.plotly_chart(plot_world_choropleth(global_result["map_ready_data"]), use_container_width=True)
            st.plotly_chart(plot_region_exposure(global_result["region_exposure_table"]), use_container_width=True)
            st.plotly_chart(plot_currency_exposure(global_result["currency_exposure_table"]), use_container_width=True)
            st.plotly_chart(plot_country_concentration(global_result["country_exposure_table"]), use_container_width=True)
            st.plotly_chart(plot_domicile_vs_revenue(global_result["domicile_vs_revenue_exposure"]), use_container_width=True)

            st.subheader("Country Exposure")
            st.dataframe(pd.DataFrame(global_result["country_exposure_table"]), use_container_width=True)

            st.subheader("Sector by Region")
            st.dataframe(pd.DataFrame(global_result["sector_region_matrix"]), use_container_width=True)

            _show_recommendations(global_result["recommendations"])

with dependency_tab:
    st.subheader("Economic Dependency Heatmap")
    st.caption("What your portfolio really depends on beneath ETF labels.")
    _show_supported_caption(dependency_supported, catalog_count)
    dependency_include_all = st.toggle(
        "Auto-include all supported dependency ETFs",
        value=True,
        key="dependency_include_all_supported",
        help="When enabled, the quick picker starts with every analyzable dependency ETF selected.",
    )
    st.caption(
        "Quick Picker shows the same practical ETF universe as overlap and global exposure, including SPY/IVV/SPLG/SCHX -> VOO, ITOT/SCHB -> VTI, VEU/ACWX/VEA/IEFA/EFA/SCHF -> IXUS, IEMG/VWO -> EEM, and ONEQ/QQQM -> QQQ."
    )
    dependency_defaults = sorted(dependency_supported) if dependency_include_all else [item["ticker"] for item in DEFAULT_DEPENDENCY_SAMPLE_PORTFOLIO]
    dependency_total_default = float(len(dependency_defaults) * 1000) if dependency_include_all else float(sum(item["amount"] for item in DEFAULT_DEPENDENCY_SAMPLE_PORTFOLIO))
    dependency_seed_portfolio = (
        [{"ticker": ticker, "amount": 1000.0} for ticker in dependency_defaults]
        if dependency_include_all
        else DEFAULT_DEPENDENCY_SAMPLE_PORTFOLIO
    )
    dependency_upload_text = _portfolio_upload_widget("dependency")
    picked_dependency_portfolio = _portfolio_picker(
        title="Quick Picker",
        supported_tickers=dependency_supported,
        catalog_df=catalog_df,
        state_key_prefix="dependency_picker",
        default_tickers=dependency_defaults,
        default_total_amount=dependency_total_default,
        default_amounts={item["ticker"]: float(item["amount"]) for item in dependency_seed_portfolio},
    )
    scenario_name_map = {scenario.name: scenario.display_name for scenario in dependency_scenarios}
    st.markdown('<div class="section-kicker">Scenario Toggles</div>', unsafe_allow_html=True)
    selected_dependency_scenarios = []
    default_selected = {"china_slowdown", "ai_boom", "usd_surge"}
    toggle_columns = st.columns(3)
    for index, scenario in enumerate(dependency_scenarios):
        with toggle_columns[index % 3]:
            enabled = st.checkbox(
                scenario.display_name,
                value=scenario.name in default_selected,
                key=f"dependency_toggle_{scenario.name}",
                help=scenario.description,
            )
            if enabled:
                selected_dependency_scenarios.append(scenario.name)
    dependency_default_portfolio = picked_dependency_portfolio or DEFAULT_DEPENDENCY_SAMPLE_PORTFOLIO
    dependency_default = json.dumps(dependency_default_portfolio, indent=2)
    with st.form("dependency_form"):
        dependency_input = st.text_area(
            "Portfolio JSON",
            value=dependency_upload_text or dependency_default,
            height=220,
        )
        dependency_submit = st.form_submit_button("Analyze Dependencies")

    if dependency_submit:
        try:
            dependency_portfolio = _parse_portfolio(dependency_input)
            dependency_result = dependency_analyzer.analyze(
                dependency_portfolio,
                selected_scenarios=selected_dependency_scenarios or None,
            ).to_dict()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unable to analyze dependency portfolio: {exc}")
        else:
            summary = dependency_result["viral_summary_card"]
            scores = dependency_result["diversification_scores"]
            _render_viral_summary_card(summary)
            _render_dependency_summary_cards(summary, scores)

            if summary.get("top_warning"):
                st.error(summary["top_warning"])
            _show_warnings(dependency_result["warnings"])

            heatmap_figure = plot_dependency_heatmap(dependency_result["heatmap_ready_data"])
            ranking_figure = plot_macro_dependency_ranking(dependency_result["macro_dependency_exposure_table"])
            map_figure = plot_dependency_world_map(dependency_result["map_ready_data"])
            comparison_figure = plot_dependency_domicile_vs_revenue(dependency_result["domicile_vs_revenue_comparison"])
            scenario_figure = plot_scenario_dashboard(dependency_result["scenario_impact_results"])
            network_figure = build_network_figure(dependency_result["network_graph_data"])

            st.markdown('<div class="section-kicker">Shareable Exports</div>', unsafe_allow_html=True)
            export_col1, export_col2, export_col3 = st.columns(3)
            with export_col1:
                _result_download_buttons(
                    dependency_result,
                    {
                        "dependency_heatmap": heatmap_figure,
                        "dependency_ranking": ranking_figure,
                    },
                    "dependency",
                )
            with export_col2:
                _figure_download_button("Download world map", map_figure, "dependency_world_map.html", "dependency_map")
                _figure_download_button(
                    "Download domicile vs revenue",
                    comparison_figure,
                    "dependency_domicile_vs_revenue.html",
                    "dependency_compare",
                )
            with export_col3:
                _figure_download_button("Download scenario dashboard", scenario_figure, "dependency_scenarios.html", "dependency_scenarios_export")
                _figure_download_button("Download network graph", network_figure, "dependency_network.html", "dependency_network_export")

            st.plotly_chart(heatmap_figure, use_container_width=True)
            st.plotly_chart(ranking_figure, use_container_width=True)

            map_col, compare_col = st.columns(2)
            with map_col:
                st.plotly_chart(map_figure, use_container_width=True)
            with compare_col:
                st.plotly_chart(comparison_figure, use_container_width=True)

            st.plotly_chart(scenario_figure, use_container_width=True)

            with st.expander("Dependency Network Graph", expanded=False):
                st.plotly_chart(network_figure, use_container_width=True)

            st.subheader("Top Macro Drivers")
            st.dataframe(pd.DataFrame(dependency_result["macro_dependency_exposure_table"]).head(15), use_container_width=True)

            st.subheader("Revenue Geography Exposure")
            st.dataframe(pd.DataFrame(dependency_result["revenue_geography_exposure_table"]), use_container_width=True)

            st.subheader("Scenario Impact Details")
            scenario_rows = []
            for scenario in dependency_result["scenario_impact_results"]:
                top_dependency = ""
                if scenario["top_contributing_dependencies"]:
                    top_dependency = scenario["top_contributing_dependencies"][0]["display_name"]
                scenario_rows.append(
                    {
                        "scenario_name": scenario["scenario_name"],
                        "display_name": scenario["display_name"],
                        "estimated_portfolio_impact_score": scenario["estimated_portfolio_impact_score"],
                        "top_dependency": top_dependency,
                    }
                )
            st.dataframe(pd.DataFrame(scenario_rows), use_container_width=True)

            st.subheader("Country Exposure")
            st.dataframe(pd.DataFrame(dependency_result["country_exposure_table"]), use_container_width=True)

            st.subheader("Sector by Region")
            st.dataframe(pd.DataFrame(dependency_result["sector_region_matrix"]), use_container_width=True)

            _show_recommendations(dependency_result["recommendations"])

with hf_tab:
    st.subheader("Hedgefund Dependency Engine")
    st.caption("Look-through exposure, macro loading, shock transmission, and graph concentration in one workflow.")
    _show_supported_caption(hf_supported, catalog_count)
    hf_include_all = st.toggle(
        "Auto-include all supported hedgefund ETFs",
        value=True,
        key="hf_include_all_supported",
        help="When enabled, the quick picker starts with every analyzable hedgefund dependency ETF selected.",
    )
    st.caption(
        "Quick Picker shows the same practical ETF universe as overlap, global exposure, and dependency heatmap, including approved proxy coverage for common core-index equivalents."
    )
    hf_defaults = sorted(hf_supported) if hf_include_all else [item["ticker"] for item in DEFAULT_HF_SAMPLE_PORTFOLIO]
    hf_total_default = float(len(hf_defaults) * 1000) if hf_include_all else float(sum(item["amount"] for item in DEFAULT_HF_SAMPLE_PORTFOLIO))
    hf_seed_portfolio = (
        [{"ticker": ticker, "amount": 1000.0} for ticker in hf_defaults]
        if hf_include_all
        else DEFAULT_HF_SAMPLE_PORTFOLIO
    )
    hf_upload_text = _portfolio_upload_widget("hf")
    picked_hf_portfolio = _portfolio_picker(
        title="Quick Picker",
        supported_tickers=hf_supported,
        catalog_df=catalog_df,
        state_key_prefix="hf_picker",
        default_tickers=hf_defaults,
        default_total_amount=hf_total_default,
        default_amounts={item["ticker"]: float(item["amount"]) for item in hf_seed_portfolio},
    )
    hf_default_selected = {"china_slowdown", "ai_boom", "usd_surge"}
    st.markdown('<div class="section-kicker">Scenario Toggles</div>', unsafe_allow_html=True)
    selected_hf_scenarios: list[str] = []
    hf_toggle_columns = st.columns(3)
    for index, scenario in enumerate(hf_scenarios):
        with hf_toggle_columns[index % 3]:
            enabled = st.checkbox(
                scenario.display_name,
                value=scenario.name in hf_default_selected,
                key=f"hf_toggle_{scenario.name}",
                help=scenario.description,
            )
            if enabled:
                selected_hf_scenarios.append(scenario.name)
    st.markdown('<div class="section-kicker">Live News Ingestion</div>', unsafe_allow_html=True)
    live_news_action_col, live_news_copy_col, live_news_control_col = st.columns([1, 2, 1])
    with live_news_action_col:
        if st.button("Fetch live headlines", key="hf_fetch_live_news", use_container_width=True):
            try:
                news_bundle = _fetch_live_news_bundle(hf_news_provider, hf_event_templates)
            except Exception as exc:  # noqa: BLE001
                st.session_state["hf_live_news_error"] = str(exc)
                st.session_state["hf_live_news_bundle"] = None
            else:
                st.session_state["hf_live_news_error"] = ""
                st.session_state["hf_live_news_bundle"] = news_bundle
                st.session_state["hf_dynamic_event_names"] = [
                    suggestion["event_name"] for suggestion in news_bundle["suggestions"]
                ]
                for suggestion in news_bundle["suggestions"]:
                    st.session_state[f"hf_event_severity_{suggestion['event_name']}"] = float(
                        suggestion["suggested_severity"]
                    )
                st.session_state["hf_headline_context"] = news_bundle["headline_context"]
    with live_news_copy_col:
        st.caption(
            "Pull current macro headlines from public RSS feeds and auto-suggest dynamic scenario overlays from the latest event mix."
        )
    with live_news_control_col:
        auto_refresh_enabled = st.toggle("Auto-refresh", value=False, key="hf_live_news_auto_refresh")
        refresh_interval = st.selectbox(
            "Refresh",
            options=[60, 180, 300, 900],
            index=2,
            format_func=lambda value: f"{value // 60} min" if value >= 60 else f"{value}s",
            key="hf_live_news_refresh_interval",
        )
    live_news_bundle = st.session_state.get("hf_live_news_bundle")
    if auto_refresh_enabled and _news_bundle_is_stale(live_news_bundle, int(refresh_interval)):
        try:
            news_bundle = _fetch_live_news_bundle(hf_news_provider, hf_event_templates)
        except Exception as exc:  # noqa: BLE001
            st.session_state["hf_live_news_error"] = str(exc)
            st.session_state["hf_live_news_bundle"] = None
        else:
            st.session_state["hf_live_news_error"] = ""
            st.session_state["hf_live_news_bundle"] = news_bundle
            st.session_state["hf_dynamic_event_names"] = [
                suggestion["event_name"] for suggestion in news_bundle["suggestions"]
            ]
            for suggestion in news_bundle["suggestions"]:
                st.session_state[f"hf_event_severity_{suggestion['event_name']}"] = float(
                    suggestion["suggested_severity"]
                )
            st.session_state["hf_headline_context"] = news_bundle["headline_context"]
        live_news_bundle = st.session_state.get("hf_live_news_bundle")
    if st.session_state.get("hf_live_news_error"):
        st.warning(f"Live news fetch failed: {st.session_state['hf_live_news_error']}")
    if live_news_bundle:
        fetched_at = live_news_bundle.get("fetched_at", "")
        if fetched_at:
            st.caption(f"Last refreshed: {fetched_at}")
        st.markdown('<div class="section-kicker">Top 5 Live Risks Today</div>', unsafe_allow_html=True)
        _render_live_risk_cards(live_news_bundle["suggestions"][:5])
        suggestion_df = pd.DataFrame(live_news_bundle["suggestions"])
        if not suggestion_df.empty:
            st.dataframe(
                suggestion_df[["display_name", "confidence_score", "suggested_severity", "matched_headline_count"]],
                use_container_width=True,
            )
        with st.expander("Fetched live headlines", expanded=False):
            st.dataframe(pd.DataFrame(live_news_bundle["headlines"]), use_container_width=True)
    if auto_refresh_enabled:
        _schedule_autorefresh(int(refresh_interval))
    st.markdown('<div class="section-kicker">Dynamic Event Scenarios</div>', unsafe_allow_html=True)
    event_name_map = {template.name: template for template in hf_event_templates}
    selected_event_names = st.multiselect(
        "Add dynamic event overlays",
        options=[template.name for template in hf_event_templates],
        default=[name for name in DEFAULT_DYNAMIC_EVENTS if name in event_name_map],
        format_func=lambda name: event_name_map[name].display_name,
        key="hf_dynamic_event_names",
    )
    dynamic_events_payload: list[dict[str, Any]] = []
    if selected_event_names:
        event_columns = st.columns(2)
        for index, event_name in enumerate(selected_event_names):
            template = event_name_map[event_name]
            with event_columns[index % 2]:
                severity = st.slider(
                    f"{template.display_name} severity",
                    min_value=0.5,
                    max_value=2.0,
                    value=float(template.default_severity),
                    step=0.1,
                    key=f"hf_event_severity_{event_name}",
                    help=template.description,
                )
                dynamic_events_payload.append({"name": event_name, "severity": float(severity)})
    hf_headline_context = st.text_area(
        "Headline / event context",
        value="War-driven shipping disruption and renewed covid outbreaks tighten global financial conditions.",
        height=100,
        key="hf_headline_context",
        help="Optional free text. Matching event keywords can auto-activate dynamic scenarios.",
    )
    hf_default_portfolio = picked_hf_portfolio or DEFAULT_HF_SAMPLE_PORTFOLIO
    hf_default = json.dumps(hf_default_portfolio, indent=2)
    with st.form("hf_form"):
        hf_input = st.text_area(
            "Portfolio JSON",
            value=hf_upload_text or hf_default,
            height=220,
        )
        hf_submit = st.form_submit_button("Analyze Hedgefund Engine")

    if hf_submit:
        try:
            hf_portfolio = _parse_portfolio(hf_input)
            hf_result = hf_analyzer.analyze(
                hf_portfolio,
                selected_scenarios=selected_hf_scenarios or None,
                dynamic_events=dynamic_events_payload or None,
                headline_context=hf_headline_context or None,
            ).to_dict()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unable to analyze hedgefund dependency portfolio: {exc}")
        else:
            hf_summary = hf_result["dashboard_summary"]
            hf_scores = hf_result["diversification_scores"]
            _render_hf_viral_summary_card(hf_summary)
            _render_hf_summary_cards(hf_summary, hf_scores)
            _show_warnings(hf_result["warnings"])

            hf_heatmap_figure = plot_hf_dependency_heatmap(hf_result["heatmap_ready_data"])
            hf_company_figure = plot_hf_company_exposure_bar(hf_result["underlying_company_exposures"])
            hf_map_figure = plot_hf_world_map(hf_result["map_ready_data"])
            hf_comparison_figure = plot_hf_domicile_vs_revenue(hf_result["domicile_vs_revenue_comparison"])
            hf_country_figure = plot_hf_country_exposure_chart(hf_result["country_exposures"])
            hf_scenario_figure = plot_hf_scenario_impact_chart(hf_result["scenario_results"])

            st.markdown('<div class="section-kicker">Shareable Exports</div>', unsafe_allow_html=True)
            hf_export_col1, hf_export_col2, hf_export_col3 = st.columns(3)
            with hf_export_col1:
                _result_download_buttons(
                    hf_result,
                    {
                        "hf_dependency_heatmap": hf_heatmap_figure,
                        "hf_company_exposures": hf_company_figure,
                    },
                    "hedgefund",
                )
            with hf_export_col2:
                _figure_download_button("Download world map", hf_map_figure, "hedgefund_world_map.html", "hf_map")
                _figure_download_button(
                    "Download domicile vs revenue",
                    hf_comparison_figure,
                    "hedgefund_domicile_vs_revenue.html",
                    "hf_compare",
                )
            with hf_export_col3:
                _figure_download_button("Download scenario impacts", hf_scenario_figure, "hedgefund_scenarios.html", "hf_scenarios")

            st.plotly_chart(hf_heatmap_figure, use_container_width=True)
            st.plotly_chart(hf_company_figure, use_container_width=True)

            hf_map_col, hf_compare_col = st.columns(2)
            with hf_map_col:
                st.plotly_chart(hf_map_figure, use_container_width=True)
            with hf_compare_col:
                st.plotly_chart(hf_comparison_figure, use_container_width=True)

            hf_country_col, hf_scenario_col = st.columns(2)
            with hf_country_col:
                st.plotly_chart(hf_country_figure, use_container_width=True)
            with hf_scenario_col:
                st.plotly_chart(hf_scenario_figure, use_container_width=True)

            st.markdown('<div class="section-kicker">Interactive Dependency Graph</div>', unsafe_allow_html=True)
            graph_control_col1, graph_control_col2, graph_control_col3 = st.columns([2, 1, 1])
            available_hf_node_types = sorted(
                {
                    str(node.get("node_type", ""))
                    for node in hf_result["graph_data"].get("nodes", [])
                    if str(node.get("node_type", ""))
                }
            )
            with graph_control_col1:
                selected_hf_node_types = st.multiselect(
                    "Node types",
                    options=available_hf_node_types,
                    default=available_hf_node_types,
                    key="hf_graph_node_types",
                    help="Filter the graph to the layers you want to explore.",
                )
            with graph_control_col2:
                hf_edge_weights = [float(edge.get("weight", 0.0)) for edge in hf_result["graph_data"].get("edges", [])]
                hf_max_edge_weight = max(hf_edge_weights) if hf_edge_weights else 0.1
                hf_min_edge_weight = st.slider(
                    "Minimum link strength",
                    min_value=0.0,
                    max_value=float(max(0.01, round(hf_max_edge_weight, 3))),
                    value=0.0,
                    step=float(max(0.001, round(hf_max_edge_weight / 20, 3))),
                    key="hf_graph_min_edge_weight",
                    help="Hide weaker links to reduce clutter and focus on the strongest pathways.",
                )
            with graph_control_col3:
                hf_layout_algorithm = st.selectbox(
                    "Layout",
                    options=["spring", "kamada_kawai", "circular"],
                    format_func=lambda value: value.replace("_", " ").title(),
                    key="hf_graph_layout",
                )
            hf_show_labels = st.checkbox(
                "Show node labels",
                value=True,
                key="hf_graph_show_labels",
                help="Turn labels off if you want a cleaner graph for panning and zooming.",
            )
            hf_network_figure = build_hf_network_figure(
                hf_result["graph_data"],
                included_node_types=selected_hf_node_types,
                min_edge_weight=hf_min_edge_weight,
                show_labels=hf_show_labels,
                layout_algorithm=hf_layout_algorithm,
            )
            st.caption("Pan, zoom, hover, and filter the graph to trace concentration paths from the portfolio through ETFs and companies into macro drivers.")
            st.plotly_chart(
                hf_network_figure,
                use_container_width=True,
                config={"scrollZoom": True, "displayModeBar": True},
            )
            _figure_download_button("Download network graph", hf_network_figure, "hedgefund_network.html", "hf_network")

            st.subheader("Top Macro Drivers")
            st.dataframe(pd.DataFrame(hf_result["dependency_exposures"]).head(15), use_container_width=True)

            st.subheader("Scenario Impact Details")
            hf_scenario_rows = []
            for scenario in hf_result["scenario_results"]:
                top_dependency = ""
                top_company = ""
                if scenario["top_contributing_dependencies"]:
                    top_dependency = scenario["top_contributing_dependencies"][0]["display_name"]
                if scenario["top_contributing_companies"]:
                    top_company = scenario["top_contributing_companies"][0]["company_name"]
                hf_scenario_rows.append(
                    {
                        "display_name": scenario["display_name"],
                        "estimated_portfolio_impact_score": scenario["estimated_portfolio_impact_score"],
                        "top_dependency": top_dependency,
                        "top_company": top_company,
                    }
                )
            st.dataframe(pd.DataFrame(hf_scenario_rows), use_container_width=True)

            applied_dynamic = hf_result["analysis_metadata"].get("applied_dynamic_scenarios", [])
            if applied_dynamic:
                st.subheader("Applied Dynamic Scenarios")
                st.dataframe(pd.DataFrame(applied_dynamic), use_container_width=True)

            st.subheader("Graph Centrality Hubs")
            centrality_tabs = st.tabs(["Companies", "Dependencies", "ETFs"])
            with centrality_tabs[0]:
                st.dataframe(pd.DataFrame(hf_result["graph_centrality"].get("company", [])).head(15), use_container_width=True)
            with centrality_tabs[1]:
                st.dataframe(pd.DataFrame(hf_result["graph_centrality"].get("dependency", [])).head(15), use_container_width=True)
            with centrality_tabs[2]:
                st.dataframe(pd.DataFrame(hf_result["graph_centrality"].get("etf", [])).head(15), use_container_width=True)

            st.subheader("Exposure Tables")
            exposure_tabs = st.tabs(["Countries", "Regions", "Currencies", "Revenue", "Overlap"])
            with exposure_tabs[0]:
                st.dataframe(pd.DataFrame(hf_result["country_exposures"]), use_container_width=True)
            with exposure_tabs[1]:
                st.dataframe(pd.DataFrame(hf_result["region_exposures"]), use_container_width=True)
            with exposure_tabs[2]:
                st.dataframe(pd.DataFrame(hf_result["currency_exposures"]), use_container_width=True)
            with exposure_tabs[3]:
                st.dataframe(pd.DataFrame(hf_result["revenue_exposures"]), use_container_width=True)
            with exposure_tabs[4]:
                st.dataframe(pd.DataFrame(hf_result["overlap_pairs"]), use_container_width=True)

            st.subheader("Sector by Region")
            st.dataframe(pd.DataFrame(hf_result["analysis_metadata"]["sector_region_matrix"]), use_container_width=True)

            _show_recommendations(hf_result["recommendations"])

with earnings_tab:
    st.subheader("EarningsClarity")
    st.caption("Plain-English quarterly clarity for long-term holders after earnings calls.")
    st.caption(f"Sample companies: {', '.join(earnings_companies)}")
    earnings_mode = st.radio(
        "Mode",
        options=["Single company", "Portfolio quarter"],
        horizontal=True,
        key="earnings_mode",
    )

    if earnings_mode == "Single company":
        picker_col1, picker_col2 = st.columns(2)
        with picker_col1:
            selected_ticker = st.selectbox("Company", options=earnings_companies, key="earnings_ticker")
        with picker_col2:
            available_quarters = sorted(
                {event.quarter for event in earnings_events if event.ticker == selected_ticker},
                reverse=True,
            )
            selected_quarter = st.selectbox("Quarter", options=available_quarters, key="earnings_quarter")
        prior_quarter = None
        if len(available_quarters) > 1:
            quarter_index = available_quarters.index(selected_quarter)
            if quarter_index + 1 < len(available_quarters):
                prior_quarter = available_quarters[quarter_index + 1]
        st.caption(f"Prior quarter comparison: {prior_quarter or 'Not available'}")
        if st.button("Analyze earnings call", key="earnings_single_analyze", use_container_width=True):
            try:
                earnings_result = earnings_analyzer.analyze_saved_call(
                    selected_ticker,
                    selected_quarter,
                    prior_quarter=prior_quarter,
                ).to_dict()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Unable to analyze earnings call: {exc}")
            else:
                _render_earnings_viral_card(earnings_result)
                _render_earnings_summary_cards(earnings_result)

                st.subheader("5-Point Summary")
                for index, bullet in enumerate(earnings_result["five_point_summary"], start=1):
                    st.write(f"{index}. {bullet}")

                evidence_col, topics_col = st.columns(2)
                with evidence_col:
                    st.subheader("Evidence")
                    st.dataframe(pd.DataFrame(earnings_result["evidence_snippets"]), use_container_width=True)
                with topics_col:
                    st.subheader("Detected Topics")
                    st.dataframe(pd.DataFrame(earnings_result["detected_topics"]), use_container_width=True)

                signal_col1, signal_col2 = st.columns(2)
                with signal_col1:
                    st.subheader("Caution Signals")
                    st.dataframe(pd.DataFrame(earnings_result["caution_signals"]), use_container_width=True)
                with signal_col2:
                    st.subheader("Positive Signals")
                    st.dataframe(pd.DataFrame(earnings_result["positive_signals"]), use_container_width=True)

                st.subheader("Long-Term Watch Items")
                for item in earnings_result["watch_items"]:
                    st.write(f"- {item}")

                st.subheader("Extended Summary")
                st.text_area(
                    "Email-ready summary",
                    value=earnings_result["extended_summary"]["email_ready"],
                    height=220,
                    key="earnings_email_ready",
                )
                st.download_button(
                    "Download earnings analysis JSON",
                    data=json.dumps(earnings_result, indent=2),
                    file_name=f"{earnings_result['ticker']}_{earnings_result['quarter']}_earnings_clarity.json",
                    mime="application/json",
                    key="earnings_result_download",
                )
    else:
        holdings_upload = st.file_uploader(
            "Upload holdings JSON",
            type=["json"],
            key="earnings_holdings_upload",
            help="Upload a JSON array like [{\"ticker\": \"AAPL\", \"shares\": 10}]",
        )
        default_holdings_text = json.dumps(DEFAULT_EARNINGS_SAMPLE_HOLDINGS, indent=2)
        quarter_choice = st.selectbox("Quarter", options=earnings_quarters, key="earnings_portfolio_quarter")
        holdings_input = st.text_area(
            "Holdings JSON",
            value=holdings_upload.getvalue().decode("utf-8") if holdings_upload else default_holdings_text,
            height=200,
            key="earnings_holdings_json",
        )
        if st.button("Analyze portfolio quarter", key="earnings_portfolio_analyze", use_container_width=True):
            try:
                holdings_payload = json.loads(holdings_input)
                holdings = validate_earnings_holdings(holdings_payload)
                portfolio_results = analyze_earnings_portfolio_quarter(earnings_analyzer, holdings, quarter_choice)
            except Exception as exc:  # noqa: BLE001
                st.error(f"Unable to analyze portfolio quarter: {exc}")
            else:
                st.subheader("Portfolio Quarter Digest")
                digest_rows = [
                    {
                        "ticker": item["ticker"],
                        "headline": item["headline_result"]["headline_classification"],
                        "tone_shift": item["tone_shift"]["tone_shift_label"],
                        "thesis_status": item["thesis_status"],
                        "confidence_score": item["confidence_score"],
                    }
                    for item in portfolio_results
                ]
                st.dataframe(pd.DataFrame(digest_rows), use_container_width=True)
                for item in portfolio_results:
                    with st.expander(f"{item['ticker']} — {item['quarter']}", expanded=False):
                        for index, bullet in enumerate(item["five_point_summary"], start=1):
                            st.write(f"{index}. {bullet}")
                        st.caption(f"Watch items: {', '.join(item['watch_items'])}")
                        st.dataframe(pd.DataFrame(item["evidence_snippets"]), use_container_width=True)

with cost_tab:
    st.subheader("True Cost of Investing")
    st.caption("Turn small annual frictions into the actual long-term dollars they may quietly cost.")
    cost_mode = st.radio(
        "Mode",
        options=["Analyze current portfolio", "Compare current vs optimized"],
        horizontal=True,
        key="cost_mode",
    )
    sample_col1, sample_col2 = st.columns(2)
    with sample_col1:
        selected_portfolio_sample = st.selectbox(
            "Portfolio sample",
            options=list(cost_portfolio_samples),
            key="cost_portfolio_sample",
        )
    with sample_col2:
        selected_assumption_sample = st.selectbox(
            "Assumption set",
            options=list(cost_assumption_samples),
            key="cost_assumption_sample",
        )

    cost_portfolio_upload = _json_upload_widget(
        "Upload current portfolio JSON",
        "cost_current",
        "Upload a holdings JSON array for the cost calculator.",
    )
    cost_assumptions_upload = _json_upload_widget(
        "Upload assumptions JSON",
        "cost_assumptions",
        "Upload a JSON object with account and behavior assumptions.",
    )
    current_default_text = Path(cost_portfolio_samples[selected_portfolio_sample]).read_text(encoding="utf-8")
    assumptions_default_text = Path(cost_assumption_samples[selected_assumption_sample]).read_text(encoding="utf-8")

    alternative_default_text = Path(DEFAULT_COST_ALTERNATIVE_PORTFOLIO_FILE).read_text(encoding="utf-8")
    alternative_upload_text = None
    if cost_mode == "Compare current vs optimized":
        alternative_upload_text = _json_upload_widget(
            "Upload alternative portfolio JSON",
            "cost_alternative",
            "Optional alternative portfolio for side-by-side cost comparison.",
        )

    with st.form("cost_form"):
        current_portfolio_input = st.text_area(
            "Current portfolio JSON",
            value=cost_portfolio_upload or current_default_text,
            height=220,
        )
        if cost_mode == "Compare current vs optimized":
            alternative_portfolio_input = st.text_area(
                "Alternative portfolio JSON",
                value=alternative_upload_text or alternative_default_text,
                height=220,
            )
        else:
            alternative_portfolio_input = ""
        assumptions_input = st.text_area(
            "Assumptions JSON",
            value=cost_assumptions_upload or assumptions_default_text,
            height=220,
        )
        cost_submit = st.form_submit_button(
            "Analyze investing costs" if cost_mode == "Analyze current portfolio" else "Compare portfolio costs"
        )

    if cost_submit:
        try:
            current_payload = json.loads(current_portfolio_input)
            current_holdings = [CostHoldingInput(**item) for item in current_payload]
            assumptions_payload = json.loads(assumptions_input)
            assumptions = CostPortfolioAssumptions(**assumptions_payload)
            if cost_mode == "Compare current vs optimized":
                alternative_payload = json.loads(alternative_portfolio_input)
                alternative_holdings = [CostHoldingInput(**item) for item in alternative_payload]
                cost_comparison = true_cost_analyzer.compare(current_holdings, alternative_holdings, assumptions).to_dict()
                current_result = cost_comparison["current"]
                alternative_result = cost_comparison["alternative"]
            else:
                cost_result = true_cost_analyzer.analyze(current_holdings, assumptions).to_dict()
                cost_comparison = None
                current_result = cost_result
                alternative_result = None
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unable to analyze investing costs: {exc}")
        else:
            _render_cost_viral_card(current_result["summary"])
            _render_cost_summary_cards(current_result)

            _show_recommendations(current_result["recommendations"])

            annual_cost_figure = plot_cost_stacked_cost_breakdown(current_result["annual_friction_breakdown"])
            cumulative_loss_figure = plot_cost_cumulative_loss_timeline(current_result["timeline"])
            gross_net_figure = plot_cost_gross_vs_net_timeline(current_result["timeline"])

            st.markdown('<div class="section-kicker">Shareable Exports</div>', unsafe_allow_html=True)
            export_col1, export_col2, export_col3 = st.columns(3)
            with export_col1:
                _result_download_buttons(
                    current_result,
                    {
                        "annual_cost_breakdown": annual_cost_figure,
                        "cumulative_loss_timeline": cumulative_loss_figure,
                    },
                    "true_cost",
                )
            with export_col2:
                _figure_download_button(
                    "Download gross vs net growth",
                    gross_net_figure,
                    "true_cost_gross_vs_net.html",
                    "true_cost_growth",
                )
                st.download_button(
                    "Download summary JSON",
                    data=json.dumps(current_result["summary"], indent=2),
                    file_name="true_cost_summary.json",
                    mime="application/json",
                    key="true_cost_summary_json",
                )
            with export_col3:
                st.download_button(
                    "Download full analysis JSON",
                    data=json.dumps(cost_comparison or current_result, indent=2),
                    file_name="true_cost_analysis.json",
                    mime="application/json",
                    key="true_cost_analysis_json",
                )

            st.plotly_chart(annual_cost_figure, use_container_width=True)
            growth_col1, growth_col2 = st.columns(2)
            with growth_col1:
                st.plotly_chart(cumulative_loss_figure, use_container_width=True)
            with growth_col2:
                st.plotly_chart(gross_net_figure, use_container_width=True)

            st.subheader("Plain-English Insights")
            for insight in current_result["insights"]:
                st.write(f"- {insight}")

            if cost_comparison:
                comparison_figure = plot_cost_comparison_chart(cost_comparison["projected_savings"])
                st.subheader("Current vs Optimized Comparison")
                st.plotly_chart(comparison_figure, use_container_width=True)
                compare_col1, compare_col2, compare_col3 = st.columns(3)
                compare_col1.metric(
                    "Ending Value Savings",
                    f"${float(cost_comparison['projected_savings']['ending_value_savings']):,.0f}",
                )
                compare_col2.metric(
                    "Current Net Ending Value",
                    f"${float(cost_comparison['projected_savings']['net_value_current']):,.0f}",
                )
                compare_col3.metric(
                    "Alternative Net Ending Value",
                    f"${float(cost_comparison['projected_savings']['net_value_alternative']):,.0f}",
                )
                st.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "category": key,
                                "ending_value_savings": value,
                            }
                            for key, value in cost_comparison["projected_savings"]["savings_by_category"].items()
                        ]
                    ).sort_values("ending_value_savings", ascending=False),
                    use_container_width=True,
                )
                for insight in cost_comparison["insights"]:
                    st.write(f"- {insight}")

            breakdown_tabs = st.tabs(["Per Holding", "Annual Breakdown", "Years 10/20/30", "Category Attribution"])
            with breakdown_tabs[0]:
                st.dataframe(pd.DataFrame(current_result["per_holding_cost_breakdown"]), use_container_width=True)
            with breakdown_tabs[1]:
                st.dataframe(pd.DataFrame(current_result["annual_friction_breakdown"]), use_container_width=True)
            with breakdown_tabs[2]:
                st.dataframe(pd.DataFrame(current_result["comparison_table"]), use_container_width=True)
            with breakdown_tabs[3]:
                st.dataframe(pd.DataFrame(current_result["dollars_lost_by_category"]), use_container_width=True)

with regime_tab:
    st.subheader("Economic Regime Translator")
    st.caption("Turn macro noise into a plain-English regime label, historical analogs, and portfolio implications.")
    regime_mode = st.radio(
        "Mode",
        options=["Classify current snapshot", "Compare current vs prior snapshot"],
        horizontal=True,
        key="regime_mode",
    )
    regime_current_upload = _json_upload_widget(
        "Upload current snapshot JSON",
        "regime_current",
        "Upload a macro snapshot JSON object.",
    )
    regime_history_upload = st.file_uploader(
        "Upload historical macro CSV",
        type=["csv"],
        key="regime_history_upload",
        help="Optional historical macro dataset for analog matching.",
    )
    regime_current_default = Path(DEFAULT_REGIME_CURRENT_FILE).read_text(encoding="utf-8")
    regime_prior_default = Path(DEFAULT_REGIME_PRIOR_FILE).read_text(encoding="utf-8")
    regime_history_default = Path(DEFAULT_REGIME_HISTORY_FILE).read_text(encoding="utf-8")
    auto_fill_from_history = st.toggle(
        "Auto-fill snapshots from latest history rows",
        value=True,
        key="regime_auto_fill_from_history",
        help="Use the latest row in the historical dataset as the current snapshot and the prior row as the comparison snapshot.",
    )
    auto_history_notice = ""
    try:
        regime_history_preview_df = pd.read_csv(io.StringIO(regime_history_upload.getvalue().decode("utf-8"))) if regime_history_upload else pd.read_csv(DEFAULT_REGIME_HISTORY_FILE)
    except Exception:  # noqa: BLE001
        regime_history_preview_df = None
    if auto_fill_from_history and regime_history_preview_df is not None and not regime_history_preview_df.empty:
        auto_current_snapshot = regime_analyzer.latest_snapshot_from_history(regime_history_preview_df).to_dict()
        auto_prior_snapshot = regime_analyzer.prior_snapshot_from_history(regime_history_preview_df).to_dict()
        regime_current_default = json.dumps(auto_current_snapshot, indent=2)
        regime_prior_default = json.dumps(auto_prior_snapshot, indent=2)
        auto_history_notice = (
            f"Auto-filled current snapshot from {auto_current_snapshot['observation_date']} "
            f"and prior snapshot from {auto_prior_snapshot['observation_date']}."
        )
    regime_prior_upload = None
    if regime_mode == "Compare current vs prior snapshot":
        regime_prior_upload = _json_upload_widget(
            "Upload prior snapshot JSON",
            "regime_prior",
            "Upload the prior macro snapshot JSON object.",
        )
    if auto_history_notice:
        st.caption(auto_history_notice)

    with st.form("regime_form"):
        regime_current_input = st.text_area(
            "Current snapshot JSON",
            value=regime_current_upload or regime_current_default,
            height=220,
        )
        if regime_mode == "Compare current vs prior snapshot":
            regime_prior_input = st.text_area(
                "Prior snapshot JSON",
                value=regime_prior_upload or regime_prior_default,
                height=220,
            )
        else:
            regime_prior_input = ""
        regime_history_input = st.text_area(
            "Historical macro CSV",
            value=regime_history_upload.getvalue().decode("utf-8") if regime_history_upload else regime_history_default,
            height=220,
        )
        regime_submit = st.form_submit_button(
            "Classify regime" if regime_mode == "Classify current snapshot" else "Compare macro snapshots"
        )

    if regime_submit:
        try:
            current_snapshot = RegimeMacroSnapshot(**json.loads(regime_current_input))
            history_df = pd.read_csv(Path(DEFAULT_REGIME_HISTORY_FILE)) if not regime_history_input.strip() else pd.read_csv(
                io.StringIO(regime_history_input)
            )
            if regime_mode == "Compare current vs prior snapshot":
                prior_snapshot = RegimeMacroSnapshot(**json.loads(regime_prior_input))
                regime_comparison = regime_analyzer.compare(current_snapshot, prior_snapshot, history_df).to_dict()
                regime_result = regime_comparison["current_analysis"]
                prior_result = regime_comparison["prior_analysis"]
            else:
                regime_comparison = None
                prior_result = None
                regime_result = regime_analyzer.classify(current_snapshot, history_df).to_dict()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unable to analyze economic regime: {exc}")
        else:
            _render_regime_viral_card(regime_result)
            _render_regime_summary_cards(regime_result)

            score_figure = build_regime_score_bar_chart(regime_result["scorecard"])
            analog_figure = build_regime_analog_similarity_chart(regime_result["historical_analogs"])

            st.markdown('<div class="section-kicker">Shareable Exports</div>', unsafe_allow_html=True)
            regime_export_col1, regime_export_col2, regime_export_col3 = st.columns(3)
            with regime_export_col1:
                _result_download_buttons(
                    regime_result,
                    {
                        "regime_scorecard": score_figure,
                        "regime_analogs": analog_figure,
                    },
                    "economic_regime",
                )
            with regime_export_col2:
                st.download_button(
                    "Download regime summary JSON",
                    data=json.dumps(regime_result["plain_english_summary"], indent=2),
                    file_name="economic_regime_summary.json",
                    mime="application/json",
                    key="regime_summary_json",
                )
            with regime_export_col3:
                st.download_button(
                    "Download full regime JSON",
                    data=json.dumps(regime_comparison or regime_result, indent=2),
                    file_name="economic_regime_analysis.json",
                    mime="application/json",
                    key="regime_full_json",
                )

            st.plotly_chart(score_figure, use_container_width=True)
            st.plotly_chart(analog_figure, use_container_width=True)

            st.subheader("Plain-English Translation")
            st.write(regime_result["plain_english_summary"]["summary_paragraph"])
            for bullet in regime_result["plain_english_summary"]["five_bullet_explanation"]:
                st.write(f"- {bullet}")

            explain_col1, explain_col2 = st.columns(2)
            with explain_col1:
                st.subheader("Primary Drivers")
                for item in regime_result["primary_drivers"]:
                    st.write(f"- {item}")
                st.subheader("Risk Flags")
                for item in regime_result["risk_flags"]:
                    st.write(f"- {item}")
            with explain_col2:
                st.subheader("Watch Items")
                for item in regime_result["watch_items"]:
                    st.write(f"- {item}")
                st.subheader("Portfolio Implications")
                st.write(regime_result["portfolio_implications"]["paragraph"])

            regime_tabs = st.tabs(["Scorecard", "Indicator States", "Historical Analogs", "Implications"])
            with regime_tabs[0]:
                st.dataframe(pd.DataFrame([regime_result["scorecard"]]).T.rename(columns={0: "value"}), use_container_width=True)
            with regime_tabs[1]:
                st.dataframe(pd.DataFrame([regime_result["indicator_states"]]).T.rename(columns={0: "state"}), use_container_width=True)
            with regime_tabs[2]:
                st.dataframe(pd.DataFrame(regime_result["historical_analogs"]), use_container_width=True)
            with regime_tabs[3]:
                implication_rows = []
                for key in ["favorable_conditions", "unfavorable_conditions", "watch_items", "risk_flags"]:
                    for value in regime_result["portfolio_implications"].get(key, []):
                        implication_rows.append({"category": key, "detail": value})
                st.dataframe(pd.DataFrame(implication_rows), use_container_width=True)

            if regime_comparison and prior_result:
                transition_figure = build_regime_transition_chart(regime_result["scorecard"], prior_result["scorecard"])
                st.subheader("Regime Change Detection")
                compare_col1, compare_col2, compare_col3 = st.columns(3)
                compare_col1.metric("Prior Regime", regime_comparison["prior_regime_label"])
                compare_col2.metric("Current Regime", regime_comparison["current_regime_label"])
                compare_col3.metric("Transition", regime_comparison["transition_label"].replace("_", " ").title())
                st.write(regime_comparison["transition_summary"])
                st.plotly_chart(transition_figure, use_container_width=True)
                st.dataframe(pd.DataFrame(regime_comparison["changed_indicators"]), use_container_width=True)

with globalgap_tab:
    st.subheader("GlobalGap")
    st.caption("Reveal the valuation, currency, and earnings-growth gap between a US-heavy portfolio and a more globally diversified one.")
    globalgap_upload = _json_upload_widget(
        "Upload GlobalGap portfolio JSON",
        "globalgap_portfolio",
        "Upload a JSON array like [{\"ticker\": \"VTI\", \"quantity\": 120, \"price\": 285.0}].",
    )
    globalgap_default = Path(GLOBALGAP_SAMPLE_PORTFOLIO_FILE).read_text(encoding="utf-8")
    with st.form("globalgap_form"):
        globalgap_input = st.text_area(
            "Portfolio JSON",
            value=globalgap_upload or globalgap_default,
            height=220,
        )
        globalgap_submit = st.form_submit_button("Run GlobalGap")

    if globalgap_submit:
        try:
            globalgap_payload = _parse_portfolio(globalgap_input)
            analysis_model = globalgap_analyzer.analyze([GlobalGapPortfolioPosition(**item) for item in globalgap_payload])
            globalgap_result = analysis_model.model_dump()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unable to run GlobalGap: {exc}")
        else:
            _render_globalgap_viral_card(globalgap_result)
            _render_globalgap_summary_cards(globalgap_result)

            exposure_figure = build_globalgap_exposure_pie(analysis_model)
            valuation_figure = build_globalgap_valuation_history_chart(analysis_model)
            dollar_figure = build_globalgap_dollar_cycle_chart(analysis_model)
            analog_figure = build_globalgap_analog_bar_chart(analysis_model)
            simulation_figure = build_globalgap_simulation_chart(analysis_model)

            st.markdown('<div class="section-kicker">Shareable Exports</div>', unsafe_allow_html=True)
            export_col1, export_col2, export_col3 = st.columns(3)
            with export_col1:
                _result_download_buttons(
                    globalgap_result,
                    {
                        "globalgap_exposure": exposure_figure,
                        "globalgap_valuation": valuation_figure,
                    },
                    "globalgap",
                )
            with export_col2:
                _figure_download_button(
                    "Download dollar-cycle chart",
                    dollar_figure,
                    "globalgap_dollar_cycle.html",
                    "globalgap_dollar_export",
                )
                _figure_download_button(
                    "Download analog chart",
                    analog_figure,
                    "globalgap_analogs.html",
                    "globalgap_analog_export",
                )
            with export_col3:
                _figure_download_button(
                    "Download simulation chart",
                    simulation_figure,
                    "globalgap_simulation.html",
                    "globalgap_simulation_export",
                )
                st.download_button(
                    "Download full GlobalGap JSON",
                    data=json.dumps(globalgap_result, indent=2),
                    file_name="globalgap_analysis.json",
                    mime="application/json",
                    key="globalgap_json_export",
                )

            st.plotly_chart(exposure_figure, use_container_width=True)
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.plotly_chart(valuation_figure, use_container_width=True)
            with chart_col2:
                st.plotly_chart(dollar_figure, use_container_width=True)
            chart_col3, chart_col4 = st.columns(2)
            with chart_col3:
                st.plotly_chart(analog_figure, use_container_width=True)
            with chart_col4:
                st.plotly_chart(simulation_figure, use_container_width=True)

            st.subheader("Plain-English Readout")
            st.write(globalgap_result["recommendation"]["plain_english_note"])
            st.write(globalgap_result["recommendation"]["diversification_benefit_note"])

            explain_col1, explain_col2 = st.columns(2)
            with explain_col1:
                st.subheader("Macro Setup")
                st.write(f"- {globalgap_result['valuation_gap']['narrative']}")
                st.write(f"- {globalgap_result['earnings_growth_gap']['narrative']}")
                st.write(f"- {globalgap_result['dollar_cycle']['narrative']}")
            with explain_col2:
                st.subheader("Suggested Adjustment")
                adjustment = globalgap_result["recommendation"]["suggested_adjustment"]
                st.write(
                    f"- Current international weight: {float(adjustment['current_international_weight']) * 100:.1f}%"
                )
                st.write(
                    f"- Suggested international weight: {float(adjustment['suggested_international_weight']) * 100:.1f}%"
                )
                st.write(f"- Example vehicles: {', '.join(adjustment['suggested_vehicle_examples'])}")
                st.write(f"- Rationale: {adjustment['rationale']}")

            globalgap_tabs = st.tabs(["Holdings", "Historical Analogs", "Simulation"])
            with globalgap_tabs[0]:
                st.dataframe(pd.DataFrame(globalgap_result["portfolio_exposure"]["holdings"]), use_container_width=True)
            with globalgap_tabs[1]:
                st.dataframe(pd.DataFrame(globalgap_result["historical_analogs"]["analogs"]), use_container_width=True)
            with globalgap_tabs[2]:
                st.dataframe(
                    pd.DataFrame(
                        [
                            globalgap_result["simulation"]["current_portfolio"],
                            globalgap_result["simulation"]["diversified_portfolio"],
                        ]
                    ),
                    use_container_width=True,
                )

with valuecheck_tab:
    st.subheader("ValueCheck")
    st.caption("Before you add another small amount, see where the valuation sits versus history, peers, and Treasury yield context.")
    st.caption(f"Supported tickers: {', '.join(valuecheck_supported)}")
    valuecheck_request_upload = _json_upload_widget(
        "Upload ValueCheck request JSON",
        "valuecheck_request",
        "Upload a JSON object like {\"ticker\": \"MSFT\", \"lookback_years\": 10, \"treasury_yield\": 0.042}.",
    )
    selected_valuecheck_ticker = st.selectbox(
        "Ticker",
        options=valuecheck_supported,
        index=valuecheck_supported.index("MSFT") if "MSFT" in valuecheck_supported else 0,
        key="valuecheck_ticker",
    )
    valuecheck_asset_type = st.selectbox(
        "Asset type",
        options=["auto", "stock", "etf"],
        index=0,
        key="valuecheck_asset_type",
    )
    valuecheck_lookback = st.slider("Lookback years", min_value=3, max_value=10, value=10, step=1, key="valuecheck_lookback")
    valuecheck_treasury = st.number_input(
        "10-year Treasury yield",
        min_value=0.0,
        max_value=0.15,
        value=0.042,
        step=0.001,
        format="%.3f",
        key="valuecheck_treasury",
    )
    valuecheck_peer_group = st.text_input(
        "Peer group override",
        value="",
        key="valuecheck_peer_group",
        help="Optional peer group override if you want to compare against a specific bundled peer set.",
    )
    default_valuecheck_request = json.dumps(
        {
            "ticker": selected_valuecheck_ticker,
            "asset_type": valuecheck_asset_type,
            "lookback_years": valuecheck_lookback,
            "treasury_yield": valuecheck_treasury,
            "peer_group": valuecheck_peer_group or None,
        },
        indent=2,
    )
    with st.form("valuecheck_form"):
        valuecheck_request_text = st.text_area(
            "ValueCheck request JSON",
            value=valuecheck_request_upload or default_valuecheck_request,
            height=220,
        )
        valuecheck_submit = st.form_submit_button("Run ValueCheck")

    if valuecheck_submit:
        try:
            valuecheck_request = json.loads(valuecheck_request_text)
            valuecheck_result = valuecheck_analyzer.analyze(
                str(valuecheck_request["ticker"]),
                lookback_years=int(valuecheck_request.get("lookback_years", 10)),
                treasury_yield=float(valuecheck_request["treasury_yield"]) if valuecheck_request.get("treasury_yield") is not None else None,
                peer_group=valuecheck_request.get("peer_group") or None,
            ).to_dict()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unable to run ValueCheck: {exc}")
        else:
            _render_valuecheck_viral_card(valuecheck_result)
            _render_valuecheck_summary_cards(valuecheck_result)

            percentile_figure = plot_valuecheck_percentile_bars(valuecheck_result["historical_comparison"])
            peer_figure = plot_valuecheck_peer_comparison(valuecheck_result["peer_comparison"])
            scorecard_figure = plot_valuecheck_scorecard(valuecheck_result)

            st.markdown('<div class="section-kicker">Shareable Exports</div>', unsafe_allow_html=True)
            export_col1, export_col2, export_col3 = st.columns(3)
            with export_col1:
                _result_download_buttons(
                    valuecheck_result,
                    {
                        "history_percentiles": percentile_figure,
                        "peer_comparison": peer_figure,
                    },
                    "valuecheck",
                )
            with export_col2:
                _figure_download_button(
                    "Download scorecard",
                    scorecard_figure,
                    "valuecheck_scorecard.html",
                    "valuecheck_scorecard_export",
                )
                st.download_button(
                    "Download markdown summary",
                    data=build_valuecheck_markdown_report(valuecheck_result),
                    file_name=f"valuecheck_{valuecheck_result['ticker'].lower()}.md",
                    mime="text/markdown",
                    key="valuecheck_markdown_export",
                )
            with export_col3:
                st.download_button(
                    "Download full ValueCheck JSON",
                    data=json.dumps(valuecheck_result, indent=2),
                    file_name=f"valuecheck_{valuecheck_result['ticker'].lower()}.json",
                    mime="application/json",
                    key="valuecheck_json_export",
                )

            score_col1, score_col2 = st.columns(2)
            with score_col1:
                st.plotly_chart(percentile_figure, use_container_width=True)
            with score_col2:
                st.plotly_chart(peer_figure, use_container_width=True)
            st.plotly_chart(scorecard_figure, use_container_width=True)

            st.subheader("Plain-English View")
            st.write(valuecheck_result["plain_english_summary"]["long_term_holder_paragraph"])
            for bullet in valuecheck_result["plain_english_summary"]["five_bullet_explanation"]:
                st.write(f"- {bullet}")

            explain_col1, explain_col2 = st.columns(2)
            with explain_col1:
                st.subheader("Implied Expectations Heuristic")
                st.write(valuecheck_result["implied_expectations_summary"]["summary"])
                st.caption(
                    f"Stretch level: {str(valuecheck_result['implied_expectations_summary']['stretch_level']).replace('_', ' ')}"
                )
                st.subheader("Watch Items")
                for item in valuecheck_result["watch_items"]:
                    st.write(f"- {item}")
            with explain_col2:
                st.subheader("Caveats")
                if valuecheck_result["caveats"]:
                    for item in valuecheck_result["caveats"]:
                        st.write(f"- {item}")
                else:
                    st.success("No major valuation caveats were triggered for this ticker.")

            valuecheck_tabs = st.tabs(["Current Metrics", "Vs Own History", "Vs Peers"])
            with valuecheck_tabs[0]:
                st.dataframe(
                    pd.DataFrame(
                        [{"metric": key, "value": value} for key, value in valuecheck_result["current_metrics"].items()]
                    ),
                    use_container_width=True,
                )
            with valuecheck_tabs[1]:
                st.dataframe(pd.DataFrame(valuecheck_result["historical_comparison"]), use_container_width=True)
            with valuecheck_tabs[2]:
                st.dataframe(pd.DataFrame(valuecheck_result["peer_comparison"]), use_container_width=True)

with moatwatch_tab:
    st.subheader("MoatWatch")
    st.caption("Track whether the competitive advantages you originally bought are strengthening, holding, or slowly eroding.")
    st.caption(f"Supported companies: {', '.join(moatwatch_supported)}")
    moat_mode = st.radio(
        "Mode",
        options=["Single company", "Watchlist quarter"],
        horizontal=True,
        key="moatwatch_mode",
    )
    moat_watchlist_upload = _json_upload_widget(
        "Upload watchlist JSON",
        "moatwatch_watchlist",
        "Upload a JSON array like [{\"ticker\": \"SBUX\"}, {\"ticker\": \"MSFT\"}].",
    )
    moat_quarter = st.selectbox(
        "Quarter",
        options=["2024Q2", "2024Q3", "2024Q4", "2025Q1", "2025Q2"],
        index=4,
        key="moatwatch_quarter",
    )

    if moat_mode == "Single company":
        moat_ticker = st.selectbox(
            "Ticker",
            options=moatwatch_supported,
            index=moatwatch_supported.index("SBUX") if "SBUX" in moatwatch_supported else 0,
            key="moatwatch_ticker",
        )
        with st.form("moatwatch_company_form"):
            moat_submit = st.form_submit_button("Analyze Moat")
        if moat_submit:
            try:
                moat_result = moatwatch_analyzer.analyze(moat_ticker, moat_quarter).to_dict()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Unable to analyze moat health: {exc}")
            else:
                _render_moatwatch_viral_card(moat_result)
                _render_moatwatch_summary_cards(moat_result)

                score_history_figure = plot_moatwatch_score_history(moat_result["historical_moat_scores"])
                signal_radar_figure = plot_moatwatch_signal_radar(moat_result["signal_breakdown"])
                peer_figure = plot_moatwatch_peer_comparison(moat_result["peer_comparison"])

                st.markdown('<div class="section-kicker">Shareable Exports</div>', unsafe_allow_html=True)
                export_col1, export_col2, export_col3 = st.columns(3)
                with export_col1:
                    _result_download_buttons(
                        moat_result,
                        {
                            "moat_score_history": score_history_figure,
                            "signal_radar": signal_radar_figure,
                        },
                        "moatwatch",
                    )
                with export_col2:
                    _figure_download_button(
                        "Download peer comparison",
                        peer_figure,
                        "moatwatch_peer_comparison.html",
                        "moatwatch_peer_export",
                    )
                    st.download_button(
                        "Download markdown summary",
                        data=build_moatwatch_markdown_report(moat_result),
                        file_name=f"moatwatch_{moat_result['ticker'].lower()}.md",
                        mime="text/markdown",
                        key="moatwatch_markdown_export",
                    )
                with export_col3:
                    st.download_button(
                        "Download full MoatWatch JSON",
                        data=json.dumps(moat_result, indent=2),
                        file_name=f"moatwatch_{moat_result['ticker'].lower()}.json",
                        mime="application/json",
                        key="moatwatch_json_export",
                    )

                history_col, radar_col = st.columns(2)
                with history_col:
                    st.plotly_chart(score_history_figure, use_container_width=True)
                with radar_col:
                    st.plotly_chart(signal_radar_figure, use_container_width=True)
                st.plotly_chart(peer_figure, use_container_width=True)

                st.subheader("Plain-English Moat Readout")
                st.write(moat_result["long_term_takeaway"])
                for bullet in moat_result["plain_english_summary"]["five_bullet_explanation"]:
                    st.write(f"- {bullet}")

                explain_col1, explain_col2 = st.columns(2)
                with explain_col1:
                    st.subheader("Alert Flags")
                    for item in moat_result["alert_flags"]:
                        st.write(f"- {item}")
                    st.subheader("Watch Items")
                    for item in moat_result["watch_items"]:
                        st.write(f"- {item}")
                with explain_col2:
                    st.subheader("Commentary Findings")
                    commentary = moat_result["commentary_findings"]
                    if commentary["negative_signals"]:
                        st.write("Negative:")
                        for item in commentary["negative_signals"]:
                            st.write(f"- {item}")
                    if commentary["positive_signals"]:
                        st.write("Positive:")
                        for item in commentary["positive_signals"]:
                            st.write(f"- {item}")
                    if commentary["supporting_snippets"]:
                        st.write("Evidence:")
                        for item in commentary["supporting_snippets"]:
                            st.write(f"- {item}")

                moat_tabs = st.tabs(["Signals", "History", "Peers"])
                with moat_tabs[0]:
                    st.dataframe(pd.DataFrame(moat_result["signal_breakdown"]), use_container_width=True)
                with moat_tabs[1]:
                    st.dataframe(pd.DataFrame(moat_result["historical_moat_scores"]), use_container_width=True)
                with moat_tabs[2]:
                    st.dataframe(pd.DataFrame(moat_result["peer_comparison"]), use_container_width=True)
    else:
        moat_watchlist_default = Path(DEFAULT_MOAT_WATCHLIST_FILE).read_text(encoding="utf-8")
        with st.form("moatwatch_watchlist_form"):
            moat_watchlist_text = st.text_area(
                "Watchlist JSON",
                value=moat_watchlist_upload or moat_watchlist_default,
                height=220,
            )
            moat_watchlist_submit = st.form_submit_button("Analyze Watchlist Quarter")
        if moat_watchlist_submit:
            try:
                moat_watchlist_payload = json.loads(moat_watchlist_text)
                moat_result = moatwatch_analyzer.analyze_watchlist(
                    [MoatWatchItem(**item) for item in moat_watchlist_payload],
                    moat_quarter,
                ).to_dict()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Unable to analyze watchlist: {exc}")
            else:
                summary = moat_result["summary"]
                cols = st.columns(4)
                cols[0].metric("Tracked Companies", int(summary["tracked_companies"]))
                cols[1].metric("Strong Green", int(summary["strong_green_count"]))
                cols[2].metric("Yellow or Worse", int(summary["yellow_or_worse_count"]))
                cols[3].metric("Quarter", summary["quarter"])

                st.subheader("Watchlist Alert Digest")
                if moat_result["alert_digest"]:
                    for item in moat_result["alert_digest"]:
                        st.write(f"- {item}")
                else:
                    st.success("No watchlist-level moat alerts triggered for this quarter.")

                st.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "ticker": item["ticker"],
                                "moat_health_label": item["moat_health_label"],
                                "moat_health_score": item["moat_health_score"],
                                "transition_label": item["transition_label"],
                                "score_change_qoq": item["score_change_qoq"],
                                "score_change_yoy": item["score_change_yoy"],
                            }
                            for item in moat_result["analyses"]
                        ]
                    ).sort_values("moat_health_score", ascending=False),
                    use_container_width=True,
                )

with harvest_tab:
    st.subheader("HarvestAlert")
    st.caption("Scan taxable-account losses, estimate tax value after friction, and pair each candidate with a similar temporary replacement ETF.")
    harvest_mode = st.radio(
        "Mode",
        options=["Sample scan", "Upload JSON inputs"],
        horizontal=True,
        key="harvest_mode",
    )
    scan_date = st.text_input("Scan date", value="2026-03-15", key="harvest_scan_date")

    sample_accounts = Path(HARVEST_ACCOUNTS_FILE).read_text(encoding="utf-8")
    sample_positions = Path(HARVEST_POSITIONS_FILE).read_text(encoding="utf-8")
    sample_lots = Path(HARVEST_LOTS_FILE).read_text(encoding="utf-8")
    sample_transactions = Path(HARVEST_TRANSACTIONS_FILE).read_text(encoding="utf-8")
    sample_assumptions = Path(HARVEST_TAX_ASSUMPTIONS_FILE).read_text(encoding="utf-8")
    sample_replacements = Path(HARVEST_REPLACEMENTS_FILE).read_text(encoding="utf-8")

    upload_accounts = _json_upload_widget("Upload accounts JSON", "harvest_accounts", "Upload brokerage account JSON.")
    upload_positions = _json_upload_widget("Upload positions JSON", "harvest_positions", "Upload current position JSON.")
    upload_lots = _json_upload_widget("Upload tax lots JSON", "harvest_lots", "Upload lot-level cost basis JSON.")
    upload_transactions = _json_upload_widget("Upload transactions JSON", "harvest_transactions", "Upload transaction history JSON.")
    upload_assumptions = _json_upload_widget("Upload tax assumptions JSON", "harvest_assumptions", "Upload tax assumptions JSON.")
    upload_replacements = _json_upload_widget("Upload replacements JSON", "harvest_replacements", "Upload replacement ETF universe JSON.")

    with st.form("harvest_form"):
        if harvest_mode == "Upload JSON inputs":
            accounts_text = st.text_area("Accounts JSON", value=upload_accounts or sample_accounts, height=140)
            positions_text = st.text_area("Positions JSON", value=upload_positions or sample_positions, height=180)
            lots_text = st.text_area("Lots JSON", value=upload_lots or sample_lots, height=180)
            transactions_text = st.text_area("Transactions JSON", value=upload_transactions or sample_transactions, height=180)
            assumptions_text = st.text_area("Tax assumptions JSON", value=upload_assumptions or sample_assumptions, height=180)
            replacements_text = st.text_area("Replacement universe JSON", value=upload_replacements or sample_replacements, height=180)
        else:
            accounts_text = sample_accounts
            positions_text = sample_positions
            lots_text = sample_lots
            transactions_text = sample_transactions
            assumptions_text = sample_assumptions
            replacements_text = sample_replacements
            st.caption("Using the bundled HarvestAlert sample dataset.")
        harvest_submit = st.form_submit_button("Scan Harvest Opportunities")

    if harvest_submit:
        try:
            harvest_result = harvest_analyzer.scan(
                accounts=[HarvestAccount(**item) for item in json.loads(accounts_text)],
                positions=[HarvestPosition(**item) for item in json.loads(positions_text)],
                lots=[HarvestTaxLot(**item) for item in json.loads(lots_text)],
                transactions=[HarvestTransaction(**item) for item in json.loads(transactions_text)],
                tax_assumptions=HarvestTaxAssumptions(**json.loads(assumptions_text)),
                replacement_universe=[HarvestReplacementSecurity(**item) for item in json.loads(replacements_text)],
                scan_date=scan_date,
            ).to_dict()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unable to run HarvestAlert: {exc}")
        else:
            _render_harvest_viral_card(harvest_result)
            _render_harvest_summary_cards(harvest_result)

            losses_figure = plot_harvest_losses(harvest_result["opportunities"])
            savings_figure = plot_harvest_tax_savings(harvest_result["opportunities"])
            similarity_figure = plot_harvest_similarity(harvest_result["opportunities"])

            st.markdown('<div class="section-kicker">Shareable Exports</div>', unsafe_allow_html=True)
            export_col1, export_col2, export_col3 = st.columns(3)
            with export_col1:
                _result_download_buttons(
                    harvest_result,
                    {
                        "harvest_losses": losses_figure,
                        "harvest_tax_savings": savings_figure,
                    },
                    "harvest_alert",
                )
            with export_col2:
                _figure_download_button(
                    "Download similarity chart",
                    similarity_figure,
                    "harvest_alert_similarity.html",
                    "harvest_similarity_export",
                )
                st.download_button(
                    "Download markdown summary",
                    data=build_harvest_markdown_report(harvest_result),
                    file_name="harvest_alert_summary.md",
                    mime="text/markdown",
                    key="harvest_markdown_export",
                )
            with export_col3:
                st.download_button(
                    "Download full HarvestAlert JSON",
                    data=json.dumps(harvest_result, indent=2),
                    file_name="harvest_alert_analysis.json",
                    mime="application/json",
                    key="harvest_json_export",
                )

            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.plotly_chart(losses_figure, use_container_width=True)
            with chart_col2:
                st.plotly_chart(savings_figure, use_container_width=True)
            st.plotly_chart(similarity_figure, use_container_width=True)

            st.subheader("Plain-English Summary")
            st.write(harvest_result["plain_english_summary"]["summary_paragraph"])
            for item in harvest_result["plain_english_summary"]["what_to_verify"]:
                st.write(f"- {item}")

            explain_col1, explain_col2 = st.columns(2)
            with explain_col1:
                st.subheader("Data Completeness Flags")
                if harvest_result["data_completeness_flags"]:
                    for item in harvest_result["data_completeness_flags"]:
                        st.write(f"- {item}")
                else:
                    st.success("No major data-completeness gaps were detected in the sample input.")
                st.subheader("Disclaimers")
                for item in harvest_result["disclaimers"]:
                    st.write(f"- {item}")
            with explain_col2:
                st.subheader("Wash-Sale Conflicts")
                if harvest_result["wash_sale_conflicts"]:
                    st.dataframe(pd.DataFrame(harvest_result["wash_sale_conflicts"]), use_container_width=True)
                else:
                    st.success("No explicit wash-sale conflicts were detected in the supplied data.")

            harvest_tabs = st.tabs(["Opportunities", "No-Action Cases", "Replacements"])
            with harvest_tabs[0]:
                st.dataframe(pd.DataFrame(harvest_result["opportunities"]), use_container_width=True)
            with harvest_tabs[1]:
                st.dataframe(pd.DataFrame(harvest_result["no_action_positions"]), use_container_width=True)
            with harvest_tabs[2]:
                st.dataframe(pd.DataFrame(harvest_result["replacement_recommendations"]), use_container_width=True)

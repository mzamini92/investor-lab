from __future__ import annotations

from typing import Any, Optional

from global_etf_exposure_map.app.config import ETF_HOLDINGS_DIR
from global_etf_exposure_map.app.models import GlobalExposureAnalysisResult
from global_etf_exposure_map.app.providers.base import HoldingsProvider
from global_etf_exposure_map.app.providers.csv_provider import CSVHoldingsProvider
from global_etf_exposure_map.app.services.exposure import (
    aggregate_dimension_exposure,
    aggregate_region_revenue_exposure,
    aggregate_underlying_company_exposures,
    build_domicile_vs_revenue,
    build_map_ready_data,
    build_sector_region_matrix,
)
from global_etf_exposure_map.app.services.geography import add_country_code, compute_country_metrics, compute_region_metrics
from global_etf_exposure_map.app.services.insights import generate_summary_insights, generate_warnings
from global_etf_exposure_map.app.services.portfolio import build_constituent_frame, compute_label_based_region_mix
from global_etf_exposure_map.app.services.recommendations import generate_recommendations
from global_etf_exposure_map.app.services.scoring import compute_economic_reality_gap, compute_global_dependence_score
from global_etf_exposure_map.app.utils.normalization import normalize_portfolio_weights
from global_etf_exposure_map.app.utils.validation import validate_portfolio


class GlobalExposureAnalyzer:
    def __init__(self, holdings_provider: Optional[HoldingsProvider] = None) -> None:
        self.holdings_provider = holdings_provider or CSVHoldingsProvider(ETF_HOLDINGS_DIR)

    def analyze(self, portfolio: list[dict[str, Any]]) -> GlobalExposureAnalysisResult:
        positions = validate_portfolio(portfolio)
        normalized_portfolio = normalize_portfolio_weights(positions)
        holdings_map = self.holdings_provider.get_many(position.ticker for position in positions)
        constituent_frame = build_constituent_frame(positions, holdings_map)

        underlying_exposures_df = aggregate_underlying_company_exposures(constituent_frame)
        country_exposure_df = aggregate_dimension_exposure(constituent_frame, "country_domicile")
        country_exposure_df = add_country_code(country_exposure_df, underlying_exposures_df)
        region_exposure_df = aggregate_dimension_exposure(constituent_frame, "region")
        currency_exposure_df = aggregate_dimension_exposure(constituent_frame, "currency")
        sector_exposure_df = aggregate_dimension_exposure(constituent_frame, "sector")
        market_cap_exposure_df = aggregate_dimension_exposure(constituent_frame, "market_cap_bucket")
        revenue_exposure_df = aggregate_region_revenue_exposure(constituent_frame)
        domicile_vs_revenue_df = build_domicile_vs_revenue(region_exposure_df, revenue_exposure_df)
        sector_region_matrix_df = build_sector_region_matrix(constituent_frame)
        map_ready_df = build_map_ready_data(country_exposure_df)

        country_metrics = compute_country_metrics(country_exposure_df)
        region_metrics = compute_region_metrics(region_exposure_df)
        label_region_mix = compute_label_based_region_mix(normalized_portfolio, holdings_map)
        economic_reality_gap = compute_economic_reality_gap(
            label_region_mix=label_region_mix,
            actual_region_exposure_df=region_exposure_df,
            domicile_vs_revenue_df=domicile_vs_revenue_df,
            region_hhi=float(region_metrics["hhi"]),
        )
        global_dependence_score, score_breakdown = compute_global_dependence_score(
            country_metrics=country_metrics,
            region_metrics=region_metrics,
            currency_exposure_df=currency_exposure_df,
            market_cap_exposure_df=market_cap_exposure_df,
            country_exposure_df=country_exposure_df,
            economic_reality_gap=economic_reality_gap,
        )

        rounded_country_metrics = {key: round(value, 6) if isinstance(value, float) else value for key, value in country_metrics.items()}
        rounded_region_metrics = {key: round(value, 6) if isinstance(value, float) else value for key, value in region_metrics.items()}
        rounded_region_metrics["score_breakdown"] = score_breakdown

        country_rows = self._round_records(country_exposure_df.to_dict(orient="records"))
        region_rows = self._round_records(region_exposure_df.to_dict(orient="records"))
        currency_rows = self._round_records(currency_exposure_df.to_dict(orient="records"))
        sector_rows = self._round_records(sector_exposure_df.to_dict(orient="records"))
        market_cap_rows = self._round_records(market_cap_exposure_df.to_dict(orient="records"))

        warnings = generate_warnings(
            normalized_portfolio=normalized_portfolio,
            country_exposure_table=country_rows,
            region_exposure_table=region_rows,
            currency_exposure_table=currency_rows,
            country_metrics=rounded_country_metrics,
            global_dependence_score=global_dependence_score,
            economic_reality_gap=economic_reality_gap,
        )
        insights = generate_summary_insights(
            country_exposure_table=country_rows,
            region_exposure_table=region_rows,
            currency_exposure_table=currency_rows,
            country_metrics=rounded_country_metrics,
            region_metrics=rounded_region_metrics,
            global_dependence_score=global_dependence_score,
            economic_reality_gap=economic_reality_gap,
        )
        recommendations = generate_recommendations(
            country_exposure_table=country_rows,
            region_exposure_table=region_rows,
            currency_exposure_table=currency_rows,
            normalized_portfolio=normalized_portfolio,
            global_dependence_score=global_dependence_score,
        )

        dashboard_summary = self._build_dashboard_summary(
            country_rows=country_rows,
            region_rows=region_rows,
            currency_rows=currency_rows,
            country_metrics=rounded_country_metrics,
            global_dependence_score=global_dependence_score,
            economic_reality_gap=economic_reality_gap,
            warnings=warnings,
        )

        return GlobalExposureAnalysisResult(
            normalized_portfolio_weights=self._round_records(normalized_portfolio),
            underlying_company_exposures=self._round_records(underlying_exposures_df.to_dict(orient="records")),
            country_exposure_table=country_rows,
            region_exposure_table=region_rows,
            currency_exposure_table=currency_rows,
            sector_exposure_table=sector_rows,
            market_cap_exposure_table=market_cap_rows,
            country_concentration_metrics=rounded_country_metrics,
            region_concentration_metrics=rounded_region_metrics,
            domicile_vs_revenue_exposure=self._round_records(domicile_vs_revenue_df.to_dict(orient="records")),
            sector_region_matrix=self._round_records(sector_region_matrix_df.to_dict(orient="records")),
            map_ready_data=self._round_records(map_ready_df.to_dict(orient="records")),
            dashboard_summary=dashboard_summary,
            global_dependence_score=global_dependence_score,
            economic_reality_gap=economic_reality_gap,
            warnings=warnings,
            summary_insights=insights,
            recommendations=recommendations,
            analysis_metadata={
                "provider": self.holdings_provider.__class__.__name__,
                "supported_etfs": self.holdings_provider.supported_etfs(),
            },
        )

    @staticmethod
    def _round_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rounded: list[dict[str, Any]] = []
        for record in records:
            normalized_record: dict[str, Any] = {}
            for key, value in record.items():
                normalized_record[key] = round(value, 6) if isinstance(value, float) else value
            rounded.append(normalized_record)
        return rounded

    @staticmethod
    def _build_dashboard_summary(
        *,
        country_rows: list[dict[str, Any]],
        region_rows: list[dict[str, Any]],
        currency_rows: list[dict[str, Any]],
        country_metrics: dict[str, Any],
        global_dependence_score: float,
        economic_reality_gap: float,
        warnings: list[str],
    ) -> dict[str, Any]:
        return {
            "top_country": country_rows[0] if country_rows else {},
            "top_region": region_rows[0] if region_rows else {},
            "top_currency": currency_rows[0] if currency_rows else {},
            "effective_countries": country_metrics["effective_count"],
            "global_dependence_score": global_dependence_score,
            "economic_reality_gap": economic_reality_gap,
            "top_warnings": warnings[:3],
        }

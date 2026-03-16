from __future__ import annotations

from typing import Any, Optional

from economic_dependency_heatmap.app.config import ETF_HOLDINGS_DIR
from economic_dependency_heatmap.app.models import DependencyAnalysisResult
from economic_dependency_heatmap.app.providers.base import DependencyDataProvider
from economic_dependency_heatmap.app.providers.csv_provider import CSVDependencyDataProvider
from economic_dependency_heatmap.app.services.dependencies import (
    aggregate_macro_dependency_exposure,
    build_dependency_network,
    build_heatmap_ready_data,
)
from economic_dependency_heatmap.app.services.exposure import (
    aggregate_dimension_exposure,
    aggregate_domicile_buckets,
    aggregate_revenue_geography_exposure,
    aggregate_underlying_company_exposures,
    build_domicile_vs_revenue,
    build_map_ready_data,
    build_sector_region_matrix,
)
from economic_dependency_heatmap.app.services.geography import add_country_code, compute_distribution_metrics
from economic_dependency_heatmap.app.services.insights import generate_summary_insights, generate_warnings
from economic_dependency_heatmap.app.services.portfolio import build_constituent_frame, compute_label_based_region_mix
from economic_dependency_heatmap.app.services.recommendations import generate_recommendations
from economic_dependency_heatmap.app.services.scenarios import compute_scenario_impacts
from economic_dependency_heatmap.app.services.scoring import (
    compute_economic_reality_gap,
    compute_global_diversification_score,
    compute_macro_dependence_score,
)
from economic_dependency_heatmap.app.utils.normalization import normalize_portfolio_weights
from economic_dependency_heatmap.app.utils.validation import validate_portfolio


class EconomicDependencyAnalyzer:
    def __init__(self, data_provider: Optional[DependencyDataProvider] = None) -> None:
        self.data_provider = data_provider or CSVDependencyDataProvider(ETF_HOLDINGS_DIR)

    def analyze(
        self,
        portfolio: list[dict[str, Any]],
        selected_scenarios: Optional[list[str]] = None,
    ) -> DependencyAnalysisResult:
        positions = validate_portfolio(portfolio)
        normalized_portfolio = normalize_portfolio_weights(positions)
        holdings_map = self.data_provider.get_many(position.ticker for position in positions)
        scenarios = self.data_provider.get_scenarios()
        constituent_frame = build_constituent_frame(positions, holdings_map)

        underlying_exposures_df = aggregate_underlying_company_exposures(constituent_frame)
        country_exposure_df = add_country_code(
            aggregate_dimension_exposure(constituent_frame, "country_domicile"),
            underlying_exposures_df,
        )
        region_exposure_df = aggregate_dimension_exposure(constituent_frame, "region")
        currency_exposure_df = aggregate_dimension_exposure(constituent_frame, "currency")
        sector_exposure_df = aggregate_dimension_exposure(constituent_frame, "sector")
        revenue_exposure_df = aggregate_revenue_geography_exposure(constituent_frame)
        dependency_exposure_df = aggregate_macro_dependency_exposure(constituent_frame)
        domicile_bucket_df = aggregate_domicile_buckets(constituent_frame)
        domicile_vs_revenue_df = build_domicile_vs_revenue(domicile_bucket_df, revenue_exposure_df)
        sector_region_matrix_df = build_sector_region_matrix(constituent_frame)
        map_ready_df = build_map_ready_data(country_exposure_df, revenue_exposure_df)
        heatmap_ready_df = build_heatmap_ready_data(dependency_exposure_df)
        network_graph_data = build_dependency_network(constituent_frame)
        scenario_results = compute_scenario_impacts(constituent_frame, scenarios, selected_names=selected_scenarios)

        country_metrics = compute_distribution_metrics(country_exposure_df)
        region_metrics = compute_distribution_metrics(region_exposure_df, top_n=(1, 3))
        currency_metrics = compute_distribution_metrics(currency_exposure_df, top_n=(1, 3))
        revenue_metrics = compute_distribution_metrics(revenue_exposure_df)
        dependency_metrics = compute_distribution_metrics(dependency_exposure_df.rename(columns={"display_name": "name"}))

        label_region_mix = compute_label_based_region_mix(normalized_portfolio, holdings_map)
        economic_reality_gap = compute_economic_reality_gap(
            normalized_portfolio=normalized_portfolio,
            label_region_mix=label_region_mix,
            revenue_exposure_df=revenue_exposure_df,
            dependency_metrics=dependency_metrics,
            region_metrics=region_metrics,
            currency_exposure_df=currency_exposure_df,
        )
        global_diversification_score, global_diversification_breakdown = compute_global_diversification_score(
            country_metrics=country_metrics,
            region_metrics=region_metrics,
            revenue_metrics=revenue_metrics,
            dependency_metrics=dependency_metrics,
            currency_metrics=currency_metrics,
            country_exposure_df=country_exposure_df,
            currency_exposure_df=currency_exposure_df,
        )
        macro_dependence_score, macro_dependence_breakdown = compute_macro_dependence_score(dependency_metrics)

        concentration_metrics = {
            "country": country_metrics,
            "region": region_metrics,
            "currency": currency_metrics,
            "revenue": revenue_metrics,
            "dependency": dependency_metrics,
        }
        diversification_scores = {
            "global_diversification_score": global_diversification_score,
            "economic_reality_gap": economic_reality_gap,
            "macro_dependence_score": macro_dependence_score,
        }
        score_breakdowns = {
            "global_diversification_breakdown": global_diversification_breakdown,
            "macro_dependence_breakdown": macro_dependence_breakdown,
        }

        country_rows = self._round_records(country_exposure_df.to_dict(orient="records"))
        region_rows = self._round_records(region_exposure_df.to_dict(orient="records"))
        currency_rows = self._round_records(currency_exposure_df.to_dict(orient="records"))
        sector_rows = self._round_records(sector_exposure_df.to_dict(orient="records"))
        revenue_rows = self._round_records(revenue_exposure_df.to_dict(orient="records"))
        dependency_rows = self._round_records(dependency_exposure_df.to_dict(orient="records"))

        warnings = generate_warnings(
            normalized_portfolio=normalized_portfolio,
            country_exposure_table=country_rows,
            revenue_exposure_table=revenue_rows,
            macro_dependency_exposure_table=dependency_rows,
            diversification_scores=diversification_scores,
            concentration_metrics=concentration_metrics,
        )
        insights = generate_summary_insights(
            country_exposure_table=country_rows,
            region_exposure_table=self._round_records(region_exposure_df.to_dict(orient="records")),
            revenue_exposure_table=revenue_rows,
            macro_dependency_exposure_table=dependency_rows,
            diversification_scores=diversification_scores,
            concentration_metrics=concentration_metrics,
        )
        recommendations = generate_recommendations(
            normalized_portfolio=normalized_portfolio,
            country_exposure_table=country_rows,
            revenue_exposure_table=revenue_rows,
            currency_exposure_table=currency_rows,
            macro_dependency_exposure_table=dependency_rows,
            diversification_scores=diversification_scores,
        )

        top_country = country_rows[0] if country_rows else {}
        top_region = self._round_records(region_exposure_df.to_dict(orient="records"))[0] if not region_exposure_df.empty else {}
        top_driver = dependency_rows[0] if dependency_rows else {}
        viral_summary_card = {
            "top_hidden_dependency": top_driver.get("display_name", ""),
            "top_country": top_country.get("name", ""),
            "top_region": top_region.get("name", ""),
            "top_macro_driver": top_driver.get("display_name", ""),
            "economic_reality_gap": economic_reality_gap,
            "global_diversification_score": global_diversification_score,
            "top_warning": warnings[0] if warnings else "",
        }

        return DependencyAnalysisResult(
            normalized_portfolio_weights=self._round_records(normalized_portfolio),
            underlying_company_exposures=self._round_records(underlying_exposures_df.to_dict(orient="records")),
            country_exposure_table=country_rows,
            region_exposure_table=self._round_records(region_exposure_df.to_dict(orient="records")),
            currency_exposure_table=currency_rows,
            sector_exposure_table=sector_rows,
            revenue_geography_exposure_table=revenue_rows,
            macro_dependency_exposure_table=dependency_rows,
            concentration_metrics={**concentration_metrics, "score_breakdowns": score_breakdowns},
            diversification_scores=diversification_scores,
            domicile_vs_revenue_comparison=self._round_records(domicile_vs_revenue_df.to_dict(orient="records")),
            scenario_impact_results=self._round_nested_list(scenario_results),
            warnings=warnings,
            summary_insights=insights,
            recommendations=recommendations,
            heatmap_ready_data=self._round_records(heatmap_ready_df.to_dict(orient="records")),
            map_ready_data=self._round_records(map_ready_df.to_dict(orient="records")),
            network_graph_data=self._round_nested_dict(network_graph_data),
            viral_summary_card=viral_summary_card,
            sector_region_matrix=self._round_records(sector_region_matrix_df.to_dict(orient="records")),
            analysis_metadata={
                "provider": self.data_provider.__class__.__name__,
                "supported_etfs": self.data_provider.supported_etfs(),
                "available_scenarios": [scenario.to_dict() for scenario in scenarios],
            },
        )

    @staticmethod
    def _round_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rounded: list[dict[str, Any]] = []
        for record in records:
            rounded.append(
                {
                    key: round(value, 6) if isinstance(value, float) else value
                    for key, value in record.items()
                }
            )
        return rounded

    def _round_nested_list(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rounded_rows: list[dict[str, Any]] = []
        for row in rows:
            rounded_row: dict[str, Any] = {}
            for key, value in row.items():
                if isinstance(value, float):
                    rounded_row[key] = round(value, 6)
                elif isinstance(value, list):
                    rounded_row[key] = self._round_nested_list(value)
                elif isinstance(value, dict):
                    rounded_row[key] = self._round_nested_dict(value)
                else:
                    rounded_row[key] = value
            rounded_rows.append(rounded_row)
        return rounded_rows

    def _round_nested_dict(self, payload: dict[str, Any]) -> dict[str, Any]:
        rounded_payload: dict[str, Any] = {}
        for key, value in payload.items():
            if isinstance(value, float):
                rounded_payload[key] = round(value, 6)
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    rounded_payload[key] = self._round_nested_list(value)
                else:
                    rounded_payload[key] = [round(item, 6) if isinstance(item, float) else item for item in value]
            elif isinstance(value, dict):
                rounded_payload[key] = self._round_nested_dict(value)
            else:
                rounded_payload[key] = value
        return rounded_payload

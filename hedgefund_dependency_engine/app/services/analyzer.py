from __future__ import annotations

from typing import Any, Optional

from hedgefund_dependency_engine.app.config import ETF_HOLDINGS_DIR
from hedgefund_dependency_engine.app.models import AnalysisResult
from hedgefund_dependency_engine.app.providers.base import EngineDataProvider
from hedgefund_dependency_engine.app.providers.csv_provider import CSVEngineDataProvider
from hedgefund_dependency_engine.app.services.dependencies import aggregate_dependency_exposures, build_heatmap_ready_data
from hedgefund_dependency_engine.app.services.exposure import (
    aggregate_dimension_exposure,
    aggregate_domicile_buckets,
    aggregate_revenue_geography_exposure,
    aggregate_underlying_company_exposures,
    build_domicile_vs_revenue,
    build_map_ready_data,
    build_sector_region_matrix,
)
from hedgefund_dependency_engine.app.services.geography import add_country_code
from hedgefund_dependency_engine.app.services.graph_analysis import build_multilayer_graph, compute_graph_centrality, graph_to_payload
from hedgefund_dependency_engine.app.services.insights import generate_summary_insights, generate_warnings
from hedgefund_dependency_engine.app.services.overlap import build_overlap_matrix
from hedgefund_dependency_engine.app.services.portfolio import build_constituent_frame, compute_label_based_region_mix
from hedgefund_dependency_engine.app.services.recommendations import generate_recommendations
from hedgefund_dependency_engine.app.services.scenarios import build_dynamic_scenarios, compute_scenario_impacts
from hedgefund_dependency_engine.app.services.scoring import (
    compute_distribution_metrics,
    compute_economic_reality_gap,
    compute_global_diversification_score,
    compute_macro_dependence_score,
)
from hedgefund_dependency_engine.app.utils.normalization import normalize_portfolio_weights
from hedgefund_dependency_engine.app.utils.validation import validate_portfolio


class HedgefundDependencyAnalyzer:
    def __init__(self, data_provider: Optional[EngineDataProvider] = None) -> None:
        self.data_provider = data_provider or CSVEngineDataProvider(ETF_HOLDINGS_DIR)

    def analyze(
        self,
        portfolio: list[dict[str, Any]],
        selected_scenarios: Optional[list[str]] = None,
        dynamic_events: Optional[list[dict[str, Any]]] = None,
        headline_context: Optional[str] = None,
    ) -> AnalysisResult:
        positions = validate_portfolio(portfolio)
        normalized_portfolio = normalize_portfolio_weights(positions)
        portfolio_weights = {row["ticker"]: float(row["portfolio_weight"]) for row in normalized_portfolio}
        holdings_map = self.data_provider.get_many(position.ticker for position in positions)
        scenarios = self.data_provider.get_scenarios()
        event_templates = self.data_provider.get_event_templates()
        frame = build_constituent_frame(positions, holdings_map)

        company_df = aggregate_underlying_company_exposures(frame)
        country_df = add_country_code(aggregate_dimension_exposure(frame, "country_domicile"), company_df)
        region_df = aggregate_dimension_exposure(frame, "region")
        sector_df = aggregate_dimension_exposure(frame, "sector")
        currency_df = aggregate_dimension_exposure(frame, "currency")
        market_cap_df = aggregate_dimension_exposure(frame, "market_cap_bucket")
        revenue_df = aggregate_revenue_geography_exposure(frame)
        dependency_df = aggregate_dependency_exposures(frame)
        domicile_bucket_df = aggregate_domicile_buckets(frame)
        domicile_vs_revenue_df = build_domicile_vs_revenue(domicile_bucket_df, revenue_df)
        map_ready_df = build_map_ready_data(country_df, revenue_df)
        heatmap_ready_df = build_heatmap_ready_data(dependency_df)
        sector_region_matrix_df = build_sector_region_matrix(frame)

        overlap_matrix, overlap_pairs = build_overlap_matrix(holdings_map, portfolio_weights)

        company_metrics = compute_distribution_metrics(company_df.rename(columns={"underlying_ticker": "name"}))
        country_metrics = compute_distribution_metrics(country_df)
        region_metrics = compute_distribution_metrics(region_df)
        dependency_metrics = compute_distribution_metrics(dependency_df.rename(columns={"display_name": "name"}))
        revenue_metrics = compute_distribution_metrics(revenue_df)
        currency_metrics = compute_distribution_metrics(currency_df)

        label_region_mix = compute_label_based_region_mix(normalized_portfolio, holdings_map)
        economic_reality_gap = compute_economic_reality_gap(
            normalized_portfolio=normalized_portfolio,
            label_region_mix=label_region_mix,
            company_metrics=company_metrics,
            country_metrics=country_metrics,
            region_metrics=region_metrics,
            dependency_metrics=dependency_metrics,
            currency_metrics=currency_metrics,
        )
        global_div_score, global_div_breakdown = compute_global_diversification_score(
            country_metrics=country_metrics,
            region_metrics=region_metrics,
            revenue_metrics=revenue_metrics,
            dependency_metrics=dependency_metrics,
            currency_metrics=currency_metrics,
            country_exposure_df=country_df,
            currency_exposure_df=currency_df,
        )
        macro_dep_score, macro_dep_breakdown = compute_macro_dependence_score(dependency_metrics)

        dynamic_scenarios = build_dynamic_scenarios(
            event_templates,
            dynamic_events=dynamic_events,
            headline_context=headline_context,
        )
        selected_static = None if not selected_scenarios else [name for name in selected_scenarios if not str(name).startswith("dynamic_")]
        active_scenarios = [
            scenario for scenario in scenarios if not selected_static or scenario.name in set(selected_static)
        ] + dynamic_scenarios
        scenario_results = compute_scenario_impacts(frame, active_scenarios)
        graph = build_multilayer_graph(frame)
        graph_payload = graph_to_payload(graph)
        graph_centrality = compute_graph_centrality(graph)

        diversification_scores = {
            "global_diversification_score": global_div_score,
            "economic_reality_gap": economic_reality_gap,
            "macro_dependence_score": macro_dep_score,
        }
        concentration_metrics = {
            "companies": company_metrics,
            "countries": country_metrics,
            "regions": region_metrics,
            "dependencies": dependency_metrics,
            "revenue": revenue_metrics,
            "currencies": currency_metrics,
            "score_breakdowns": {
                "global_diversification_breakdown": global_div_breakdown,
                "macro_dependence_breakdown": macro_dep_breakdown,
            },
        }

        company_rows = self._round_records(company_df.to_dict(orient="records"))
        country_rows = self._round_records(country_df.to_dict(orient="records"))
        region_rows = self._round_records(region_df.to_dict(orient="records"))
        sector_rows = self._round_records(sector_df.to_dict(orient="records"))
        currency_rows = self._round_records(currency_df.to_dict(orient="records"))
        market_cap_rows = self._round_records(market_cap_df.to_dict(orient="records"))
        revenue_rows = self._round_records(revenue_df.to_dict(orient="records"))
        dependency_rows = self._round_records(dependency_df.to_dict(orient="records"))

        warnings = generate_warnings(
            normalized_portfolio=normalized_portfolio,
            dependency_exposures=dependency_rows,
            country_exposures=country_rows,
            overlap_pairs=overlap_pairs,
            diversification_scores=diversification_scores,
            graph_centrality=graph_centrality,
        )
        insights = generate_summary_insights(
            dependency_exposures=dependency_rows,
            revenue_exposures=revenue_rows,
            graph_centrality=graph_centrality,
            diversification_scores=diversification_scores,
        )
        recommendations = generate_recommendations(
            normalized_portfolio=normalized_portfolio,
            dependency_exposures=dependency_rows,
            country_exposures=country_rows,
            currency_exposures=currency_rows,
            overlap_pairs=overlap_pairs,
            diversification_scores=diversification_scores,
        )

        summary = {
            "top_country": country_rows[0] if country_rows else {},
            "top_region": region_rows[0] if region_rows else {},
            "top_dependency": dependency_rows[0] if dependency_rows else {},
            "top_warning": warnings[0] if warnings else "",
            "economic_reality_gap": economic_reality_gap,
            "global_diversification_score": global_div_score,
        }

        return AnalysisResult(
            normalized_portfolio_weights=self._round_records(normalized_portfolio),
            underlying_company_exposures=company_rows,
            country_exposures=country_rows,
            region_exposures=region_rows,
            sector_exposures=sector_rows,
            currency_exposures=currency_rows,
            market_cap_exposures=market_cap_rows,
            revenue_exposures=revenue_rows,
            dependency_exposures=dependency_rows,
            overlap_pairs=self._round_nested_list(overlap_pairs),
            overlap_matrix=self._round_nested_dict(overlap_matrix),
            concentration_metrics=concentration_metrics,
            diversification_scores=diversification_scores,
            scenario_results=self._round_nested_list(scenario_results),
            graph_data=self._round_nested_dict(graph_payload),
            graph_centrality=self._round_nested_dict(graph_centrality),
            warnings=warnings,
            summary_insights=insights,
            recommendations=recommendations,
            heatmap_ready_data=self._round_records(heatmap_ready_df.to_dict(orient="records")),
            map_ready_data=self._round_records(map_ready_df.to_dict(orient="records")),
            dashboard_summary=summary,
            domicile_vs_revenue_comparison=self._round_records(domicile_vs_revenue_df.to_dict(orient="records")),
            analysis_metadata={
                "provider": self.data_provider.__class__.__name__,
                "supported_etfs": self.data_provider.supported_etfs(),
                "available_scenarios": [scenario.to_dict() for scenario in scenarios],
                "available_event_templates": [template.to_dict() for template in event_templates],
                "applied_dynamic_scenarios": [scenario.to_dict() for scenario in dynamic_scenarios],
                "headline_context": headline_context or "",
                "sector_region_matrix": self._round_records(sector_region_matrix_df.to_dict(orient="records")),
            },
        )

    @staticmethod
    def _round_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [{key: round(value, 6) if isinstance(value, float) else value for key, value in record.items()} for record in records]

    def _round_nested_list(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rounded_rows: list[dict[str, Any]] = []
        for row in rows:
            rounded: dict[str, Any] = {}
            for key, value in row.items():
                if isinstance(value, float):
                    rounded[key] = round(value, 6)
                elif isinstance(value, list):
                    rounded[key] = self._round_nested_list(value)
                elif isinstance(value, dict):
                    rounded[key] = self._round_nested_dict(value)
                else:
                    rounded[key] = value
            rounded_rows.append(rounded)
        return rounded_rows

    def _round_nested_dict(self, payload: dict[str, Any]) -> dict[str, Any]:
        rounded: dict[str, Any] = {}
        for key, value in payload.items():
            if isinstance(value, float):
                rounded[key] = round(value, 6)
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    rounded[key] = self._round_nested_list(value)
                else:
                    rounded[key] = [round(item, 6) if isinstance(item, float) else item for item in value]
            elif isinstance(value, dict):
                rounded[key] = self._round_nested_dict(value)
            else:
                rounded[key] = value
        return rounded

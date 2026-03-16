from __future__ import annotations

from typing import Any
from typing import Optional, Union

from etf_overlap.analytics.exposure import (
    aggregate_dimension_exposure,
    aggregate_underlying_exposures,
    build_constituent_frame,
    compute_mag7_exposure,
    normalize_portfolio,
)
from etf_overlap.analytics.overlap import build_overlap_matrix
from etf_overlap.analytics.scoring import (
    compute_concentration_metrics,
    compute_dimension_hhi,
    compute_diversification_score,
    compute_hidden_concentration_score,
    compute_portfolio_redundancy_index,
)
from etf_overlap.analytics.suggestions import generate_suggestions
from etf_overlap.analytics.warnings import generate_warnings
from etf_overlap.config import DEFAULT_DATA_DIR
from etf_overlap.exceptions import ValidationError
from etf_overlap.models import AnalysisResult, PortfolioPosition
from etf_overlap.providers.base import HoldingsProvider
from etf_overlap.providers.csv_provider import CSVHoldingsProvider


class PortfolioAnalyzer:
    """Main orchestration layer for ETF portfolio look-through analysis."""

    def __init__(self, holdings_provider: Optional[HoldingsProvider] = None) -> None:
        self.holdings_provider = holdings_provider or CSVHoldingsProvider(DEFAULT_DATA_DIR)

    def analyze(self, portfolio: Union[list[dict[str, Any]], list[PortfolioPosition]]) -> AnalysisResult:
        positions = self._validate_portfolio(portfolio)
        normalized_portfolio = normalize_portfolio(positions)
        portfolio_weights = {row["ticker"]: float(row["portfolio_weight"]) for row in normalized_portfolio}
        holdings_map = self.holdings_provider.get_many(position.ticker for position in positions)

        constituent_frame = build_constituent_frame(positions, holdings_map)
        underlying_exposures_df = aggregate_underlying_exposures(constituent_frame)
        sector_exposures_df = aggregate_dimension_exposure(constituent_frame, "sector")
        country_exposures_df = aggregate_dimension_exposure(constituent_frame, "country")
        style_exposures_df = aggregate_dimension_exposure(constituent_frame, "style_box")

        overlap_matrix, overlap_pairs = build_overlap_matrix(holdings_map, portfolio_weights)
        concentration_metrics = compute_concentration_metrics(underlying_exposures_df)
        sector_hhi, sector_effective_count = compute_dimension_hhi(sector_exposures_df)
        country_hhi, country_effective_count = compute_dimension_hhi(country_exposures_df)
        style_hhi, style_effective_count = compute_dimension_hhi(style_exposures_df)

        naive_holdings_count = sum(len(holdings.holdings) for holdings in holdings_map.values())
        redundancy_index = compute_portfolio_redundancy_index(overlap_pairs, portfolio_weights)
        practical_overlap_total = sum(float(pair["practical_overlap_contribution"]) for pair in overlap_pairs)
        hidden_concentration_score = compute_hidden_concentration_score(
            effective_number_of_stocks=float(concentration_metrics["effective_number_of_stocks"]),
            naive_holdings_count=naive_holdings_count,
            top_10_concentration=float(concentration_metrics["top_10_concentration"]),
            sector_hhi=sector_hhi,
            redundancy_index=redundancy_index,
            practical_overlap_total=practical_overlap_total,
        )
        diversification_score, score_breakdown = compute_diversification_score(
            top_10_concentration=float(concentration_metrics["top_10_concentration"]),
            sector_effective_count=sector_effective_count,
            country_effective_count=country_effective_count,
            style_effective_count=style_effective_count,
            effective_number_of_stocks=float(concentration_metrics["effective_number_of_stocks"]),
            naive_holdings_count=naive_holdings_count,
            redundancy_index=redundancy_index,
        )
        mag7_exposure = compute_mag7_exposure(underlying_exposures_df)

        concentration_metrics.update(
            {
                "naive_lookthrough_holdings_count": naive_holdings_count,
                "sector_hhi": sector_hhi,
                "sector_effective_count": sector_effective_count,
                "country_hhi": country_hhi,
                "country_effective_count": country_effective_count,
                "style_hhi": style_hhi,
                "style_effective_count": style_effective_count,
            }
        )

        sector_exposures = self._round_records(sector_exposures_df.to_dict(orient="records"))
        country_exposures = self._round_records(country_exposures_df.to_dict(orient="records"))
        style_exposures = self._round_records(style_exposures_df.to_dict(orient="records"))
        warnings = generate_warnings(
            naive_holdings_count=naive_holdings_count,
            concentration_metrics=concentration_metrics,
            sector_exposures=sector_exposures,
            country_exposures=country_exposures,
            overlap_pairs=overlap_pairs,
            mag7_exposure=mag7_exposure,
            hidden_concentration_score=hidden_concentration_score,
            diversification_score=diversification_score,
        )
        suggestions = generate_suggestions(
            overlap_pairs=overlap_pairs,
            sector_exposures=sector_exposures,
            country_exposures=country_exposures,
            mag7_exposure=mag7_exposure,
            concentration_metrics=concentration_metrics,
            normalized_portfolio=normalized_portfolio,
        )

        summary_insights = self._build_summary_insights(
            concentration_metrics=concentration_metrics,
            sector_exposures=sector_exposures,
            country_exposures=country_exposures,
            mag7_exposure=mag7_exposure,
            redundancy_index=redundancy_index,
        )

        underlying_exposures = self._round_records(underlying_exposures_df.to_dict(orient="records"))
        rounded_overlap_pairs = self._round_records(overlap_pairs)
        rounded_concentration_metrics = {
            key: round(value, 6) if isinstance(value, float) else value for key, value in concentration_metrics.items()
        }
        rounded_normalized_portfolio = self._round_records(normalized_portfolio)
        rounded_overlap_matrix = {
            etf_a: {etf_b: self._round_record(metrics) for etf_b, metrics in row.items()}
            for etf_a, row in overlap_matrix.items()
        }

        return AnalysisResult(
            normalized_portfolio=rounded_normalized_portfolio,
            underlying_exposures=underlying_exposures,
            overlap_matrix=rounded_overlap_matrix,
            overlap_pairs=rounded_overlap_pairs,
            concentration_metrics=rounded_concentration_metrics,
            sector_exposures=sector_exposures,
            country_exposures=country_exposures,
            style_exposures=style_exposures,
            mag7_exposure=mag7_exposure,
            warnings=warnings,
            summary_insights=summary_insights,
            optimization_suggestions=suggestions,
            diversification_score=diversification_score,
            hidden_concentration_score=hidden_concentration_score,
            redundancy_index=redundancy_index,
            score_breakdown=score_breakdown,
            analysis_metadata={"provider": self.holdings_provider.__class__.__name__},
        )

    @staticmethod
    def _validate_portfolio(
        portfolio: Union[list[dict[str, Any]], list[PortfolioPosition]]
    ) -> list[PortfolioPosition]:
        if not portfolio:
            raise ValidationError("Portfolio cannot be empty.")

        positions = [
            position if isinstance(position, PortfolioPosition) else PortfolioPosition(**position)
            for position in portfolio
        ]

        seen: set[str] = set()
        for position in positions:
            if position.ticker in seen:
                raise ValidationError(f"Duplicate ETF ticker in portfolio: {position.ticker}")
            seen.add(position.ticker)
        return positions

    @staticmethod
    def _round_record(record: dict[str, Any]) -> dict[str, Any]:
        rounded: dict[str, Any] = {}
        for key, value in record.items():
            if isinstance(value, float):
                rounded[key] = round(value, 6)
            elif isinstance(value, list):
                rounded[key] = value
            else:
                rounded[key] = value
        return rounded

    def _round_records(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self._round_record(record) for record in records]

    @staticmethod
    def _build_summary_insights(
        *,
        concentration_metrics: dict[str, Any],
        sector_exposures: list[dict[str, Any]],
        country_exposures: list[dict[str, Any]],
        mag7_exposure: dict[str, Any],
        redundancy_index: float,
    ) -> list[str]:
        insights = [
            f"Top 10 underlying companies account for {float(concentration_metrics['top_10_concentration']):.1%} of the portfolio.",
            f"Effective number of stocks: {float(concentration_metrics['effective_number_of_stocks']):.1f}.",
            f"Portfolio redundancy index: {redundancy_index:.1f}/100.",
            f"Magnificent 7 exposure totals {float(mag7_exposure['total']):.1%}.",
        ]
        if sector_exposures:
            insights.append(
                f"Largest sector exposure is {sector_exposures[0]['name']} at {float(sector_exposures[0]['exposure']):.1%}."
            )
        if country_exposures:
            insights.append(
                f"Largest country exposure is {country_exposures[0]['name']} at {float(country_exposures[0]['exposure']):.1%}."
            )
        return insights

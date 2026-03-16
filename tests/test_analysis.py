from __future__ import annotations

import math

from etf_overlap.engine import PortfolioAnalyzer
from etf_overlap.models import ETFHoldings, HoldingRecord
from etf_overlap.providers.mock_provider import MockHoldingsProvider


def build_test_provider() -> MockHoldingsProvider:
    return MockHoldingsProvider(
        {
            "ETF1": ETFHoldings(
                ticker="ETF1",
                holdings=[
                    HoldingRecord("AAA", "Alpha", 0.5, "Technology", "United States", 1_000_000_000, "Blend"),
                    HoldingRecord("BBB", "Beta", 0.5, "Healthcare", "United States", 800_000_000, "Value"),
                ],
            ),
            "ETF2": ETFHoldings(
                ticker="ETF2",
                holdings=[
                    HoldingRecord("AAA", "Alpha", 0.25, "Technology", "United States", 1_000_000_000, "Blend"),
                    HoldingRecord("CCC", "Gamma", 0.75, "Industrials", "Germany", 900_000_000, "Growth"),
                ],
            ),
            "ETF3": ETFHoldings(
                ticker="ETF3",
                holdings=[
                    HoldingRecord("DDD", "Delta", 0.5, "Financials", "Canada", 700_000_000, "Value"),
                    HoldingRecord("EEE", "Epsilon", 0.5, "Utilities", "Japan", 600_000_000, "Blend"),
                ],
            ),
        }
    )


def test_underlying_exposure_calculation() -> None:
    analyzer = PortfolioAnalyzer(build_test_provider())
    result = analyzer.analyze(
        [
            {"ticker": "ETF1", "amount": 60},
            {"ticker": "ETF2", "amount": 40},
        ]
    )

    exposure_map = {row["stock_ticker"]: row["exposure"] for row in result.underlying_exposures}
    assert math.isclose(exposure_map["AAA"], 0.4, rel_tol=1e-9)
    assert math.isclose(exposure_map["BBB"], 0.3, rel_tol=1e-9)
    assert math.isclose(exposure_map["CCC"], 0.3, rel_tol=1e-9)


def test_overlap_matrix_logic() -> None:
    analyzer = PortfolioAnalyzer(build_test_provider())
    result = analyzer.analyze(
        [
            {"ticker": "ETF1", "amount": 60},
            {"ticker": "ETF2", "amount": 40},
        ]
    )

    pair = next(row for row in result.overlap_pairs if row["etf_a"] == "ETF1" and row["etf_b"] == "ETF2")
    assert math.isclose(pair["weighted_overlap"], 0.25, rel_tol=1e-9)
    assert math.isclose(pair["unweighted_overlap"], 0.5, rel_tol=1e-9)
    assert math.isclose(pair["practical_overlap_contribution"], 0.1, rel_tol=1e-9)
    assert result.overlap_matrix["ETF1"]["ETF2"]["weighted_overlap"] == pair["weighted_overlap"]


def test_effective_number_of_stocks() -> None:
    analyzer = PortfolioAnalyzer(build_test_provider())
    result = analyzer.analyze(
        [
            {"ticker": "ETF1", "amount": 60},
            {"ticker": "ETF2", "amount": 40},
        ]
    )

    expected_hhi = (0.4**2) + (0.3**2) + (0.3**2)
    expected_effective = 1.0 / expected_hhi
    assert math.isclose(result.concentration_metrics["hhi"], expected_hhi, rel_tol=1e-6)
    assert math.isclose(
        result.concentration_metrics["effective_number_of_stocks"],
        expected_effective,
        rel_tol=1e-6,
    )


def test_diversification_score_rewards_broader_portfolio() -> None:
    analyzer = PortfolioAnalyzer(build_test_provider())
    concentrated = analyzer.analyze([{"ticker": "ETF1", "amount": 100}])
    diversified = analyzer.analyze(
        [
            {"ticker": "ETF1", "amount": 34},
            {"ticker": "ETF2", "amount": 33},
            {"ticker": "ETF3", "amount": 33},
        ]
    )

    assert 0.0 <= concentrated.diversification_score <= 100.0
    assert 0.0 <= diversified.diversification_score <= 100.0
    assert diversified.diversification_score > concentrated.diversification_score


def test_warning_generation_for_overlap_and_concentration() -> None:
    analyzer = PortfolioAnalyzer(build_test_provider())
    result = analyzer.analyze(
        [
            {"ticker": "ETF1", "amount": 90},
            {"ticker": "ETF2", "amount": 10},
        ]
    )

    joined_warnings = " | ".join(result.warnings)
    assert "effective number of stocks" in joined_warnings
    assert "top 8 companies" in joined_warnings or "Top-10 concentration" in joined_warnings


import math

from hedgefund_dependency_engine.app.models import ETFHoldings, HoldingRecord, MacroScenario
from hedgefund_dependency_engine.app.providers.mock_provider import MockEngineDataProvider
from hedgefund_dependency_engine.app.services.analyzer import HedgefundDependencyAnalyzer


def build_provider() -> MockEngineDataProvider:
    return MockEngineDataProvider(
        {
            "ETF1": ETFHoldings(
                ticker="ETF1",
                label_region="North America",
                label_focus="US Core",
                holdings=[
                    HoldingRecord(
                        "ETF1", "AAA", "Alpha", 0.6, "Technology", "United States", "North America", "USD", "Mega Cap", "USA",
                        revenue_us=0.5, revenue_europe=0.2, revenue_china=0.1, revenue_apac_ex_china=0.1, revenue_japan=0.03, revenue_latam=0.03, revenue_mea=0.02, revenue_other=0.02,
                        us_consumer=0.4, china_demand=0.2, europe_demand=0.2, ai_capex=0.8, cloud_spending=0.7, global_semiconductors=0.9, industrial_capex=0.1, energy_prices=0.0, healthcare_spending=0.0, financial_conditions=0.1, usd_strength=0.4, interest_rate_sensitivity=0.3, emerging_market_growth=0.2,
                    ),
                    HoldingRecord(
                        "ETF1", "BBB", "Beta", 0.4, "Healthcare", "United States", "North America", "USD", "Large Cap", "USA",
                        revenue_us=0.7, revenue_europe=0.1, revenue_china=0.05, revenue_apac_ex_china=0.05, revenue_japan=0.03, revenue_latam=0.03, revenue_mea=0.02, revenue_other=0.02,
                        us_consumer=0.2, china_demand=0.1, europe_demand=0.1, ai_capex=0.0, cloud_spending=0.0, global_semiconductors=0.0, industrial_capex=0.0, energy_prices=0.0, healthcare_spending=0.8, financial_conditions=0.1, usd_strength=0.2, interest_rate_sensitivity=0.2, emerging_market_growth=0.1,
                    ),
                ],
            ),
            "ETF2": ETFHoldings(
                ticker="ETF2",
                label_region="Europe",
                label_focus="Europe",
                holdings=[
                    HoldingRecord(
                        "ETF2", "AAA", "Alpha", 0.2, "Technology", "United States", "North America", "USD", "Mega Cap", "USA",
                        revenue_us=0.5, revenue_europe=0.2, revenue_china=0.1, revenue_apac_ex_china=0.1, revenue_japan=0.03, revenue_latam=0.03, revenue_mea=0.02, revenue_other=0.02,
                        us_consumer=0.4, china_demand=0.2, europe_demand=0.2, ai_capex=0.8, cloud_spending=0.7, global_semiconductors=0.9, industrial_capex=0.1, energy_prices=0.0, healthcare_spending=0.0, financial_conditions=0.1, usd_strength=0.4, interest_rate_sensitivity=0.3, emerging_market_growth=0.2,
                    ),
                    HoldingRecord(
                        "ETF2", "CCC", "Gamma", 0.8, "Industrials", "Germany", "Europe", "EUR", "Large Cap", "DEU",
                        revenue_us=0.2, revenue_europe=0.4, revenue_china=0.1, revenue_apac_ex_china=0.1, revenue_japan=0.05, revenue_latam=0.05, revenue_mea=0.05, revenue_other=0.05,
                        us_consumer=0.1, china_demand=0.2, europe_demand=0.5, ai_capex=0.1, cloud_spending=0.0, global_semiconductors=0.0, industrial_capex=0.7, energy_prices=0.1, healthcare_spending=0.0, financial_conditions=0.1, usd_strength=0.5, interest_rate_sensitivity=0.3, emerging_market_growth=0.2,
                    ),
                ],
            ),
        },
        scenarios=[
            MacroScenario(
                name="ai_boom",
                display_name="AI Boom",
                description="AI spending rises.",
                shock_weights={"ai_capex": 1.0, "cloud_spending": 0.5, "global_semiconductors": 0.5},
            )
        ],
    )


def test_company_exposure_propagation() -> None:
    result = HedgefundDependencyAnalyzer(build_provider()).analyze([{"ticker": "ETF1", "amount": 50}, {"ticker": "ETF2", "amount": 50}])
    exposure_map = {row["underlying_ticker"]: row["exposure"] for row in result.underlying_company_exposures}
    assert math.isclose(exposure_map["AAA"], 0.4, rel_tol=1e-9)
    assert math.isclose(exposure_map["BBB"], 0.2, rel_tol=1e-9)
    assert math.isclose(exposure_map["CCC"], 0.4, rel_tol=1e-9)


def test_revenue_exposure_aggregation() -> None:
    result = HedgefundDependencyAnalyzer(build_provider()).analyze([{"ticker": "ETF1", "amount": 50}, {"ticker": "ETF2", "amount": 50}])
    revenue_map = {row["name"]: row["exposure"] for row in result.revenue_exposures}
    expected_us = (0.4 * 0.5) + (0.2 * 0.7) + (0.4 * 0.2)
    assert math.isclose(revenue_map["United States"], expected_us, rel_tol=1e-9)

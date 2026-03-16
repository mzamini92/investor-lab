from hedgefund_dependency_engine.app.models import ETFHoldings, HoldingRecord
from hedgefund_dependency_engine.app.providers.mock_provider import MockEngineDataProvider
from hedgefund_dependency_engine.app.services.analyzer import HedgefundDependencyAnalyzer


def build_concentrated_provider() -> MockEngineDataProvider:
    return MockEngineDataProvider(
        {
            "US1": ETFHoldings(
                ticker="US1",
                label_region="North America",
                label_focus="US Growth",
                holdings=[
                    HoldingRecord(
                        "US1", "AAA", "Alpha", 1.0, "Technology", "United States", "North America", "USD", "Mega Cap", "USA",
                        revenue_us=0.75, revenue_europe=0.08, revenue_china=0.06, revenue_apac_ex_china=0.04, revenue_japan=0.02, revenue_latam=0.02, revenue_mea=0.01, revenue_other=0.02,
                        us_consumer=0.7, china_demand=0.15, europe_demand=0.1, ai_capex=0.9, cloud_spending=0.8, global_semiconductors=0.8, industrial_capex=0.1, energy_prices=0.0, healthcare_spending=0.0, financial_conditions=0.1, usd_strength=0.2, interest_rate_sensitivity=0.4, emerging_market_growth=0.1,
                    )
                ],
            )
        }
    )


def build_diversified_provider() -> MockEngineDataProvider:
    return MockEngineDataProvider(
        {
            "A": ETFHoldings(
                ticker="A",
                label_region="North America",
                label_focus="US Core",
                holdings=[
                    HoldingRecord(
                        "A", "AAA", "Alpha", 1.0, "Technology", "United States", "North America", "USD", "Mega Cap", "USA",
                        revenue_us=0.45, revenue_europe=0.2, revenue_china=0.1, revenue_apac_ex_china=0.1, revenue_japan=0.04, revenue_latam=0.04, revenue_mea=0.03, revenue_other=0.04,
                        us_consumer=0.4, china_demand=0.2, europe_demand=0.2, ai_capex=0.5, cloud_spending=0.4, global_semiconductors=0.4, industrial_capex=0.1, energy_prices=0.0, healthcare_spending=0.0, financial_conditions=0.1, usd_strength=0.3, interest_rate_sensitivity=0.3, emerging_market_growth=0.2,
                    )
                ],
            ),
            "B": ETFHoldings(
                ticker="B",
                label_region="Europe",
                label_focus="Europe",
                holdings=[
                    HoldingRecord(
                        "B", "BBB", "Beta", 1.0, "Industrials", "Germany", "Europe", "EUR", "Large Cap", "DEU",
                        revenue_us=0.2, revenue_europe=0.45, revenue_china=0.1, revenue_apac_ex_china=0.08, revenue_japan=0.04, revenue_latam=0.05, revenue_mea=0.03, revenue_other=0.05,
                        us_consumer=0.1, china_demand=0.2, europe_demand=0.6, ai_capex=0.1, cloud_spending=0.0, global_semiconductors=0.0, industrial_capex=0.7, energy_prices=0.1, healthcare_spending=0.0, financial_conditions=0.1, usd_strength=0.5, interest_rate_sensitivity=0.2, emerging_market_growth=0.2,
                    )
                ],
            ),
            "C": ETFHoldings(
                ticker="C",
                label_region="Emerging Markets",
                label_focus="EM",
                holdings=[
                    HoldingRecord(
                        "C", "CCC", "Gamma", 1.0, "Financials", "India", "Emerging Markets", "INR", "Large Cap", "IND",
                        revenue_us=0.12, revenue_europe=0.1, revenue_china=0.18, revenue_apac_ex_china=0.18, revenue_japan=0.03, revenue_latam=0.1, revenue_mea=0.12, revenue_other=0.17,
                        us_consumer=0.08, china_demand=0.3, europe_demand=0.08, ai_capex=0.0, cloud_spending=0.0, global_semiconductors=0.0, industrial_capex=0.1, energy_prices=0.0, healthcare_spending=0.0, financial_conditions=0.6, usd_strength=0.6, interest_rate_sensitivity=0.5, emerging_market_growth=0.8,
                    )
                ],
            ),
        }
    )


def test_scores_reward_broader_distribution() -> None:
    concentrated = HedgefundDependencyAnalyzer(build_concentrated_provider()).analyze([{"ticker": "US1", "amount": 100}])
    diversified = HedgefundDependencyAnalyzer(build_diversified_provider()).analyze([{"ticker": "A", "amount": 34}, {"ticker": "B", "amount": 33}, {"ticker": "C", "amount": 33}])
    assert diversified.diversification_scores["global_diversification_score"] > concentrated.diversification_scores["global_diversification_score"]
    assert diversified.diversification_scores["macro_dependence_score"] < concentrated.diversification_scores["macro_dependence_score"]

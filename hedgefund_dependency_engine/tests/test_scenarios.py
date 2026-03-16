import math

from hedgefund_dependency_engine.app.models import EventTemplate
from hedgefund_dependency_engine.app.providers.mock_provider import MockEngineDataProvider
from hedgefund_dependency_engine.app.services.analyzer import HedgefundDependencyAnalyzer
from hedgefund_dependency_engine.tests.test_exposure import build_provider


def test_scenario_impact_logic() -> None:
    result = HedgefundDependencyAnalyzer(build_provider()).analyze(
        [{"ticker": "ETF1", "amount": 50}, {"ticker": "ETF2", "amount": 50}],
        selected_scenarios=["ai_boom"],
    )
    scenario = result.scenario_results[0]
    expected = ((0.4 * 0.8) + (0.4 * 0.1)) * 1.0
    expected += ((0.4 * 0.7) + (0.4 * 0.0)) * 0.5
    expected += ((0.4 * 0.9) + (0.4 * 0.0)) * 0.5
    assert math.isclose(scenario["estimated_portfolio_impact_score"], expected, rel_tol=1e-9)
    assert scenario["top_contributing_etfs"][0]["etf_ticker"] == "ETF1"


def test_dynamic_event_template_from_headline() -> None:
    base_provider = build_provider()
    provider = MockEngineDataProvider(
        holdings_map={ticker: base_provider.get_holdings(ticker) for ticker in base_provider.supported_etfs()},
        scenarios=base_provider.get_scenarios(),
        event_templates=[
            EventTemplate(
                name="pandemic_wave",
                display_name="Pandemic Wave",
                description="Pandemic disruption returns.",
                trigger_keywords=["covid", "pandemic", "lockdown"],
                default_severity=1.0,
                shock_weights={
                    "us_consumer": -0.6,
                    "healthcare_spending": 0.5,
                    "financial_conditions": -0.5,
                },
            )
        ],
    )
    result = HedgefundDependencyAnalyzer(provider).analyze(
        [{"ticker": "ETF1", "amount": 50}, {"ticker": "ETF2", "amount": 50}],
        headline_context="Covid lockdown fears are rising again.",
    )
    scenario_names = [scenario["scenario_name"] for scenario in result.scenario_results]
    assert "dynamic_pandemic_wave" in scenario_names
    assert result.analysis_metadata["applied_dynamic_scenarios"][0]["name"] == "dynamic_pandemic_wave"

from hedgefund_dependency_engine.app.models import EventTemplate, NewsHeadline
from hedgefund_dependency_engine.app.services.live_news import headlines_to_context, suggest_dynamic_events_from_headlines


def test_live_news_event_suggestion_matching() -> None:
    headlines = [
        NewsHeadline(
            title="Covid outbreak fears rise as shipping disruption spreads",
            source="Mock News",
            link="https://example.com/1",
            query_group="health",
        ),
        NewsHeadline(
            title="War escalation pushes oil shock and sanctions risk higher",
            source="Mock News",
            link="https://example.com/2",
            query_group="geopolitics",
        ),
    ]
    templates = [
        EventTemplate(
            name="pandemic_wave",
            display_name="Pandemic Wave",
            description="Pandemic disruption returns.",
            trigger_keywords=["covid", "pandemic", "lockdown", "outbreak"],
            default_severity=1.0,
            shock_weights={"us_consumer": -0.6, "healthcare_spending": 0.5},
        ),
        EventTemplate(
            name="war_supply_shock",
            display_name="War / Supply Shock",
            description="Conflict-driven supply chain stress.",
            trigger_keywords=["war", "sanctions", "shipping", "oil shock"],
            default_severity=1.0,
            shock_weights={"energy_prices": 0.9, "usd_strength": 0.4},
        ),
    ]

    suggestions = suggest_dynamic_events_from_headlines(headlines, templates)
    suggestion_names = [suggestion["event_name"] for suggestion in suggestions]
    assert "pandemic_wave" in suggestion_names
    assert "war_supply_shock" in suggestion_names
    assert headlines_to_context(headlines).startswith("Covid outbreak fears")

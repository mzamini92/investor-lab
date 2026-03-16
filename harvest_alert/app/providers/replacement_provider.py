from harvest_alert.app.providers.brokerage_provider import LocalBrokerageProvider


class LocalReplacementProvider(LocalBrokerageProvider):
    """Thin wrapper for future replacement-universe integrations."""

class ETFOverlapError(Exception):
    """Base error for ETF overlap analysis."""


class HoldingsNotFoundError(ETFOverlapError):
    """Raised when holdings for an ETF cannot be found."""


class ValidationError(ETFOverlapError):
    """Raised when portfolio or holdings inputs are invalid."""


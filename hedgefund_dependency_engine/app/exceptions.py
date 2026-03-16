class HedgefundDependencyError(Exception):
    """Base exception for the hedge-fund-grade dependency engine."""


class ValidationError(HedgefundDependencyError):
    """Raised when inputs fail validation."""


class HoldingsNotFoundError(HedgefundDependencyError):
    """Raised when ETF holdings data cannot be found."""


class NewsProviderError(HedgefundDependencyError):
    """Raised when live news ingestion fails."""

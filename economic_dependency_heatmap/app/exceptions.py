class EconomicDependencyError(Exception):
    """Base exception for the Economic Dependency Heatmap feature."""


class ValidationError(EconomicDependencyError):
    """Raised when inputs fail validation."""


class HoldingsNotFoundError(EconomicDependencyError):
    """Raised when ETF holdings data cannot be found."""

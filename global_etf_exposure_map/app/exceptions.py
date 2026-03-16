class GlobalExposureError(Exception):
    """Base exception for the Global ETF Exposure Map feature."""


class ValidationError(GlobalExposureError):
    """Raised when inputs fail validation."""


class HoldingsNotFoundError(GlobalExposureError):
    """Raised when ETF holdings data cannot be found."""


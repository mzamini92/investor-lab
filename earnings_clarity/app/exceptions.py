class EarningsClarityError(Exception):
    """Base exception for EarningsClarity."""


class ValidationError(EarningsClarityError):
    """Raised when request or data validation fails."""


class TranscriptNotFoundError(EarningsClarityError):
    """Raised when a transcript file cannot be found."""


class EarningsEventNotFoundError(EarningsClarityError):
    """Raised when earnings metadata cannot be found."""

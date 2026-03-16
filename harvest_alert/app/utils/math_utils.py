from __future__ import annotations

from typing import Optional


def safe_divide(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    if numerator is None or denominator in {None, 0}:
        return None
    return numerator / denominator


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))

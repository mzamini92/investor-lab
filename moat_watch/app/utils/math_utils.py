from __future__ import annotations

from typing import Optional


def safe_divide(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    if numerator is None or denominator in {None, 0}:
        return None
    return numerator / denominator


def safe_change(current: Optional[float], prior: Optional[float]) -> Optional[float]:
    if current is None or prior is None:
        return None
    return current - prior


def safe_pct_change(current: Optional[float], prior: Optional[float]) -> Optional[float]:
    if current is None or prior in {None, 0}:
        return None
    return (current / prior) - 1.0


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))

from __future__ import annotations

import math


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def normalize_to_score(value: float, lower_bound: float, upper_bound: float, *, invert: bool = False) -> float:
    if math.isclose(upper_bound, lower_bound):
        return 50.0
    ratio = (value - lower_bound) / (upper_bound - lower_bound)
    if invert:
        ratio = 1.0 - ratio
    return clamp(ratio * 100.0, 0.0, 100.0)

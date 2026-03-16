from __future__ import annotations


def annual_to_monthly_rate(annual_rate: float) -> float:
    if annual_rate <= -1.0:
        raise ValueError("annual_rate must be greater than -100%")
    return (1.0 + annual_rate) ** (1.0 / 12.0) - 1.0


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator

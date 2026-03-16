from __future__ import annotations


def safe_divide(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in {None, 0}:
        return None
    return numerator / denominator


def premium_discount(current: float | None, peer_median: float | None) -> float | None:
    if current is None or peer_median in {None, 0}:
        return None
    return (current / peer_median) - 1.0

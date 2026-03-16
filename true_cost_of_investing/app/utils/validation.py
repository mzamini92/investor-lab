from __future__ import annotations

from typing import Iterable


def validate_positive(value: float, label: str) -> None:
    if value <= 0:
        raise ValueError(f"{label} must be positive.")


def ensure_non_empty(items: Iterable[object], label: str) -> None:
    if not list(items):
        raise ValueError(f"{label} cannot be empty.")

from __future__ import annotations

from datetime import datetime


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def days_between(later: str, earlier: str) -> int:
    return (parse_date(later) - parse_date(earlier)).days

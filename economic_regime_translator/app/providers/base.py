from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class DataProvider(ABC):
    @abstractmethod
    def load(self, path: Path) -> Any:
        raise NotImplementedError

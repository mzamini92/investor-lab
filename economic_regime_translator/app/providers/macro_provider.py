from __future__ import annotations

import json
from pathlib import Path

from economic_regime_translator.app.models import MacroSnapshot
from economic_regime_translator.app.providers.base import DataProvider


class MacroSnapshotProvider(DataProvider):
    def load(self, path: Path) -> MacroSnapshot:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Snapshot JSON must be an object.")
        return MacroSnapshot(**payload)

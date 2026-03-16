from __future__ import annotations

from harvest_alert.app.utils.constants import RISK_PENALTIES
from harvest_alert.app.utils.math_utils import clamp


def score_opportunity(
    *,
    net_benefit: float,
    similarity_score: float | None,
    wash_sale_risk_level: str,
    drift_penalty: float,
) -> float:
    benefit_component = min(net_benefit / 10.0, 60.0)
    similarity_component = (similarity_score or 0.0) * 0.35
    risk_penalty = RISK_PENALTIES.get(wash_sale_risk_level, 20.0)
    return round(clamp(benefit_component + similarity_component - drift_penalty - risk_penalty, 0.0, 100.0), 2)

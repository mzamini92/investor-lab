from __future__ import annotations

from typing import Any

from harvest_alert.app.models import HarvestOpportunity, Position, ReplacementSecurity, TaxAssumptions, TaxLot
from harvest_alert.app.services.alerts import build_alert_text
from harvest_alert.app.services.ranking import score_opportunity
from harvest_alert.app.services.replacements import recommend_replacements
from harvest_alert.app.services.tax_estimator import estimate_lot_benefit, estimate_position_level_benefit
from harvest_alert.app.services.wash_sale import screen_wash_sale_conflicts


def scan_position_opportunities(
    *,
    position: Position,
    lots: list[TaxLot],
    assumptions: TaxAssumptions,
    replacement_universe: list[ReplacementSecurity],
    transactions,
    accounts,
    scan_date: str,
) -> tuple[list[HarvestOpportunity], list[dict[str, Any]], list[dict[str, Any]]]:
    opportunities: list[HarvestOpportunity] = []
    no_action: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []

    position_lots = [lot for lot in lots if lot.account_id == position.account_id and lot.ticker == position.ticker]
    replacement_rows = recommend_replacements(position.ticker, replacement_universe)
    best_replacement = replacement_rows[0] if replacement_rows else None
    replacement_model = next((item for item in replacement_universe if best_replacement and item.ticker == best_replacement["ticker"]), None)

    if position_lots:
        for lot in position_lots:
            benefit = estimate_lot_benefit(lot, assumptions)
            if benefit["harvestable_loss"] < assumptions.minimum_loss_dollar_threshold:
                no_action.append({"ticker": position.ticker, "account_id": position.account_id, "lot_id": lot.lot_id, "reason": "Loss below threshold."})
                continue
            if benefit["estimated_tax_savings"] < assumptions.minimum_tax_savings_threshold:
                no_action.append({"ticker": position.ticker, "account_id": position.account_id, "lot_id": lot.lot_id, "reason": "Estimated tax savings too small after thresholds."})
                continue
            if best_replacement is None:
                no_action.append({"ticker": position.ticker, "account_id": position.account_id, "lot_id": lot.lot_id, "reason": "No clean replacement candidate available."})
                continue
            wash = screen_wash_sale_conflicts(
                ticker=position.ticker,
                proposed_sale_date=scan_date,
                transactions=transactions,
                accounts=accounts,
                replacement=replacement_model,
            )
            if wash["conflict_transactions"]:
                conflicts.extend(wash["conflict_transactions"])
            drift_penalty = max(0.0, 100.0 - float(best_replacement["similarity_score"])) * 0.15
            opp_score = score_opportunity(
                net_benefit=benefit["net_estimated_benefit"],
                similarity_score=best_replacement["similarity_score"],
                wash_sale_risk_level=wash["wash_sale_risk_level"],
                drift_penalty=drift_penalty,
            )
            opportunities.append(
                HarvestOpportunity(
                    ticker=position.ticker,
                    account_id=position.account_id,
                    lot_id=lot.lot_id,
                    harvestable_loss=benefit["harvestable_loss"],
                    loss_pct_from_basis=benefit["loss_pct_from_basis"],
                    tax_rate_used=benefit["tax_rate_used"],
                    estimated_tax_savings=benefit["estimated_tax_savings"],
                    transaction_cost_estimate=benefit["transaction_cost_estimate"],
                    net_estimated_benefit=benefit["net_estimated_benefit"],
                    wash_sale_risk_level=wash["wash_sale_risk_level"],
                    conflict_summary=wash["explanation"],
                    recommended_replacement=best_replacement,
                    replacement_similarity_score=best_replacement["similarity_score"],
                    exposure_drift_summary=best_replacement["strategy_preservation_summary"],
                    hold_days_recommendation=assumptions.holding_period_days_for_replacement,
                    opportunity_score=opp_score,
                    alert_text=build_alert_text(
                        ticker=position.ticker,
                        harvestable_loss=benefit["harvestable_loss"],
                        estimated_tax_savings=benefit["estimated_tax_savings"],
                        replacement_ticker=best_replacement["ticker"],
                        hold_days=assumptions.holding_period_days_for_replacement,
                        risk_summary=wash["explanation"],
                        drift_summary=best_replacement["strategy_preservation_summary"],
                    ),
                    applicable_term=lot.short_term_or_long_term or "unknown",
                )
            )
    else:
        benefit = estimate_position_level_benefit(position, assumptions)
        if benefit["harvestable_loss"] < assumptions.minimum_loss_dollar_threshold:
            no_action.append({"ticker": position.ticker, "account_id": position.account_id, "reason": "Position loss below threshold."})
        elif benefit["estimated_tax_savings"] < assumptions.minimum_tax_savings_threshold:
            no_action.append({"ticker": position.ticker, "account_id": position.account_id, "reason": "Position savings estimate below threshold."})
        else:
            no_action.append({"ticker": position.ticker, "account_id": position.account_id, "reason": "No lot detail supplied; manual position-level review recommended."})

    return opportunities, no_action, conflicts

from __future__ import annotations

from dataclasses import asdict
from typing import Optional

from harvest_alert.app.config import DEFAULT_SCAN_DATE
from harvest_alert.app.models import Account, HarvestScanResult, Position, ReplacementSecurity, TaxAssumptions, TaxLot, Transaction
from harvest_alert.app.providers.base import BrokerageDataProvider
from harvest_alert.app.providers.brokerage_provider import LocalBrokerageProvider
from harvest_alert.app.services.harvesting import scan_position_opportunities
from harvest_alert.app.services.normalization import normalize_brokerage_data


class HarvestAlertAnalyzer:
    def __init__(self, provider: Optional[BrokerageDataProvider] = None) -> None:
        self.provider = provider or LocalBrokerageProvider()

    def scan(
        self,
        *,
        accounts: list[Account],
        positions: list[Position],
        lots: list[TaxLot],
        transactions: list[Transaction],
        tax_assumptions: TaxAssumptions,
        replacement_universe: list[ReplacementSecurity],
        scan_date: str = DEFAULT_SCAN_DATE,
    ) -> HarvestScanResult:
        normalized = normalize_brokerage_data(
            accounts=accounts,
            positions=positions,
            lots=lots,
            transactions=transactions,
            scan_date=scan_date,
        )
        opportunities = []
        no_action_positions = []
        wash_conflicts = []

        for position in normalized["positions"]:
            if position.account_id not in normalized["taxable_accounts"]:
                continue
            if (position.unrealized_gain_loss or 0.0) >= 0:
                no_action_positions.append(
                    {
                        "ticker": position.ticker,
                        "account_id": position.account_id,
                        "reason": "Position is not currently at a loss.",
                    }
                )
                continue
            found, skipped, conflicts = scan_position_opportunities(
                position=position,
                lots=normalized["lots"],
                assumptions=tax_assumptions,
                replacement_universe=replacement_universe,
                transactions=normalized["transactions"],
                accounts=normalized["account_map"],
                scan_date=scan_date,
            )
            opportunities.extend(found)
            no_action_positions.extend(skipped)
            wash_conflicts.extend(conflicts)

        ranked = sorted(opportunities, key=lambda item: (-item.opportunity_score, -item.net_estimated_benefit))
        opportunity_rows = [asdict(item) for item in ranked]
        summary_top = opportunity_rows[0] if opportunity_rows else None
        total_tax_savings = round(sum(item.estimated_tax_savings for item in ranked), 2)
        total_net_benefit = round(sum(item.net_estimated_benefit for item in ranked), 2)

        if summary_top:
            summary_paragraph = (
                f"Top opportunity: {summary_top['ticker']} in {summary_top['account_id']} with an estimated "
                f"${float(summary_top['estimated_tax_savings']):,.0f} tax benefit and "
                f"${float(summary_top['net_estimated_benefit']):,.0f} net benefit after friction."
            )
        else:
            summary_paragraph = "No harvest opportunities currently clear the configured thresholds in the supplied taxable data."

        return HarvestScanResult(
            scan_date=scan_date,
            accounts_scanned=[account.account_id for account in accounts],
            opportunities=opportunity_rows,
            no_action_positions=no_action_positions,
            wash_sale_conflicts=wash_conflicts,
            replacement_recommendations=[row["recommended_replacement"] for row in opportunity_rows if row["recommended_replacement"]],
            estimated_total_tax_savings=total_tax_savings,
            estimated_total_net_benefit=total_net_benefit,
            data_completeness_flags=normalized["data_completeness_flags"],
            disclaimers=[
                "This tool provides educational estimates, not tax advice.",
                "Wash-sale rules can be fact-specific and depend on complete account visibility.",
                "Users should confirm with a tax professional when necessary.",
            ],
            plain_english_summary={
                "top_opportunity": summary_top,
                "summary_paragraph": summary_paragraph,
                "what_to_verify": [
                    "Check for recent or scheduled identical-ticker buys in all linked accounts.",
                    "Confirm the replacement fund still matches your strategy after the 31-day window.",
                    "Review tax assumptions and whether short-term or long-term treatment applies.",
                ],
            },
            visualization_data={
                "harvestable_losses_by_position": [
                    {"ticker": row["ticker"], "harvestable_loss": row["harvestable_loss"]} for row in opportunity_rows
                ],
                "estimated_tax_savings_by_opportunity": [
                    {"ticker": row["ticker"], "estimated_tax_savings": row["estimated_tax_savings"]} for row in opportunity_rows
                ],
                "similarity_score_comparison": [
                    {"ticker": row["ticker"], "replacement_similarity_score": row["replacement_similarity_score"]} for row in opportunity_rows
                ],
                "wash_sale_risk_dashboard": [
                    {"ticker": row["ticker"], "wash_sale_risk_level": row["wash_sale_risk_level"]} for row in opportunity_rows
                ],
            },
        )

    def sample_scan(self) -> HarvestScanResult:
        return self.scan(
            accounts=self.provider.get_accounts(),
            positions=self.provider.get_positions(),
            lots=self.provider.get_lots(),
            transactions=self.provider.get_transactions(),
            tax_assumptions=self.provider.get_tax_assumptions(),
            replacement_universe=self.provider.get_replacements(),
            scan_date=DEFAULT_SCAN_DATE,
        )

    def evaluate_single_position(
        self,
        *,
        position: Position,
        lots: list[TaxLot],
        transactions: list[Transaction],
        tax_assumptions: TaxAssumptions,
        replacement_universe: list[ReplacementSecurity],
        account: Optional[Account] = None,
        scan_date: str = DEFAULT_SCAN_DATE,
    ) -> HarvestScanResult:
        account_list = [account] if account else [Account(account_id=position.account_id, account_name=position.account_id, account_type="taxable_brokerage", taxable_flag=True)]
        return self.scan(
            accounts=account_list,
            positions=[position],
            lots=lots,
            transactions=transactions,
            tax_assumptions=tax_assumptions,
            replacement_universe=replacement_universe,
            scan_date=scan_date,
        )

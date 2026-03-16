from __future__ import annotations

from globalgap.app.dollar_cycle import analyze_dollar_cycle
from globalgap.app.earnings import analyze_earnings_growth_gap
from globalgap.app.historical import analyze_historical_analogs
from globalgap.app.models import GlobalGapAnalysis, MacroDataSnapshot, PortfolioPosition, VisualizationData
from globalgap.app.portfolio import analyze_portfolio_exposure
from globalgap.app.recommendation import build_recommendation
from globalgap.app.simulation import run_diversification_simulation
from globalgap.app.valuation import analyze_valuation_gap


class GlobalGapAnalyzer:
    def analyze(self, positions: list[PortfolioPosition]) -> GlobalGapAnalysis:
        exposure = analyze_portfolio_exposure(positions)
        valuation_gap, valuation_history = analyze_valuation_gap()
        earnings_gap, _earnings_history = analyze_earnings_growth_gap()
        dollar_cycle, dollar_history = analyze_dollar_cycle()
        analogs = analyze_historical_analogs(valuation_gap, valuation_history)
        simulation, _adjustment, _asset_returns = run_diversification_simulation(exposure)
        recommendation = build_recommendation(exposure, valuation_gap, earnings_gap, dollar_cycle, analogs, simulation)

        visualization_data = VisualizationData(
            exposure_pie=[
                {"label": "US", "weight": round(exposure.portfolio_us_weight, 6)},
                {"label": "International", "weight": round(exposure.portfolio_international_weight, 6)},
            ],
            valuation_history=[
                {
                    "date": row.date.date().isoformat(),
                    "us_forward_pe": round(float(row.us_forward_pe), 2),
                    "international_forward_pe": round(float(row.international_forward_pe), 2),
                }
                for row in valuation_history.itertuples(index=False)
            ],
            dollar_history=[
                {
                    "date": row.date.date().isoformat(),
                    "dxy": round(float(row.dxy), 2),
                    "reer": round(float(row.reer), 2),
                }
                for row in dollar_history.itertuples(index=False)
            ],
            analog_bars=[
                {
                    "date": analog.date,
                    "following_5y_intl_minus_us_ann_pct": analog.following_5y_intl_minus_us_ann_pct,
                }
                for analog in analogs.analogs
            ],
            simulation_bars=[
                dict(simulation.current_portfolio.model_dump(), portfolio=simulation.current_portfolio.label),
                dict(simulation.diversified_portfolio.model_dump(), portfolio=simulation.diversified_portfolio.label),
            ],
        )

        return GlobalGapAnalysis(
            portfolio_exposure=exposure,
            valuation_gap=valuation_gap,
            earnings_growth_gap=earnings_gap,
            dollar_cycle=dollar_cycle,
            historical_analogs=analogs,
            simulation=simulation,
            recommendation=recommendation,
            visualization_data=visualization_data,
        )

    def macro_snapshot(self) -> MacroDataSnapshot:
        valuation_gap, _ = analyze_valuation_gap()
        earnings_gap, _ = analyze_earnings_growth_gap()
        dollar_cycle, _ = analyze_dollar_cycle()
        return MacroDataSnapshot(
            valuation_gap=valuation_gap,
            earnings_growth_gap=earnings_gap,
            dollar_cycle=dollar_cycle,
        )

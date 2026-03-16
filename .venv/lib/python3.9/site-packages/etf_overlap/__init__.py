"""ETF Hidden Overlap & Concentration Detector."""

from etf_overlap.engine import PortfolioAnalyzer


def create_app():
    from etf_overlap.api import create_app as _create_app

    return _create_app()


__all__ = ["PortfolioAnalyzer", "create_app"]

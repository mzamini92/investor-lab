# ETF Analytics Platform

This repository is a multi-product fintech analytics workspace built around a shared Streamlit dashboard and a set of standalone Python MVPs.

It started as an ETF overlap tool and now includes a broader suite for:

- ETF overlap and false-diversification detection
- global exposure mapping
- economic dependency and macro-driver analysis
- earnings-call clarity summaries
- long-horizon investing cost analysis
- macro regime translation
- valuation context
- moat-health tracking
- tax-loss harvesting alerts

The shared app is designed to make these tools usable together, while each feature also ships as its own standalone Python package with its own CLI, API, tests, and README.

## What Lives Here

- Shared dashboard: [streamlit_app.py](streamlit_app.py)
- Shared entry point: [main.py](main.py)
- Shared package config: [pyproject.toml](pyproject.toml)
- Core ETF overlap API package: [etf_overlap](/etf_overlap/)
- Shared sample holdings data: [data](/data)

## Feature Docs

Each major feature has its own markdown documentation:

- Global ETF Exposure Map: [global_etf_exposure_map/README.md](/global_etf_exposure_map/README.md)
- ETF Overlap / core platform: this root guide, [README.md](/README.md)
- Economic Dependency Heatmap: [economic_dependency_heatmap/README.md](/economic_dependency_heatmap/README.md)
- Hedgefund Dependency Engine: [hedgefund_dependency_engine/README.md](/hedgefund_dependency_engine/README.md)
- EarningsClarity: [earnings_clarity/README.md](/earnings_clarity/README.md)
- True Cost of Investing: [true_cost_of_investing/README.md](/true_cost_of_investing/README.md)
- Economic Regime Translator: [economic_regime_translator/README.md](/economic_regime_translator/README.md)
- ValueCheck: [value_check/README.md](/value_check/README.md)
- MoatWatch: [moat_watch/README.md](/moat_watch/README.md)
- HarvestAlert: [harvest_alert/README.md](/harvest_alert/README.md)

## Shared Dashboard

Run the unified app from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install '.[dev]'
streamlit run streamlit_app.py
```

The dashboard currently includes ten tabs:

1. `Overlap Detector`
2. `Global Exposure Map`
3. `Economic Dependency Heatmap`
4. `Hedgefund Dependency Engine`
5. `EarningsClarity`
6. `True Cost of Investing`
7. `Economic Regime Translator`
8. `ValueCheck`
9. `MoatWatch`
10. `HarvestAlert`

The app supports sample-mode workflows plus JSON upload or paste flows for the feature areas that use user-provided inputs.

## Quickstart

From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install '.[dev]'
pytest
uvicorn etf_overlap.api:app --reload
streamlit run streamlit_app.py
```

For the original ETF overlap CLI:

```bash
python main.py --portfolio sample_portfolio.json --pretty
```

## Shared API

The root FastAPI app is still exposed through:

```bash
uvicorn etf_overlap.api:app --reload
```

That shared API includes the overlap engine plus unified endpoints for the additional platform features that have been wired into the main service over time.

## Standalone Products

Each feature package can also be run independently. Examples:

```bash
python global_etf_exposure_map/main.py --portfolio global_etf_exposure_map/sample_portfolio.json --pretty
python economic_dependency_heatmap/main.py --portfolio economic_dependency_heatmap/sample_portfolio.json --pretty
python hedgefund_dependency_engine/main.py --portfolio hedgefund_dependency_engine/sample_portfolio.json --pretty
python earnings_clarity/main.py analyze-portfolio --holdings earnings_clarity/app/data/holdings/sample_holdings.json --quarter 2025Q4
python true_cost_of_investing/main.py analyze --portfolio true_cost_of_investing/app/data/portfolios/sample_high_fee_portfolio.json --assumptions true_cost_of_investing/app/data/assumptions/taxable_account.json
python economic_regime_translator/main.py classify --snapshot economic_regime_translator/app/data/samples/current_snapshot.json --history economic_regime_translator/app/data/historical/historical_macro.csv --with-analogs
python value_check/main.py check --ticker MSFT
python moat_watch/main.py analyze --ticker SBUX --quarter 2025Q2 --pretty
python harvest_alert/main.py scan --pretty
```

For full usage, assumptions, data format, and endpoint details, use the feature README links above.

## Repository Layout

Top-level structure:

- [etf_overlap](/etf_overlap): original overlap engine and shared API home
- [global_etf_exposure_map](/global_etf_exposure_map): look-through geography and revenue exposure mapping
- [economic_dependency_heatmap](/economic_dependency_heatmap): dependency heatmaps and macro-driver summaries
- [hedgefund_dependency_engine](/hedgefund_dependency_engine): deeper propagation, shock transmission, graph analysis, and live-news-assisted macro overlays
- [earnings_clarity](/earnings_clarity): plain-English quarterly earnings interpretation
- [true_cost_of_investing](/true_cost_of_investing): long-term fee, tax drag, and friction-cost modeling
- [economic_regime_translator](/economic_regime_translator): macro snapshot classification and historical analogs
- [value_check](/value_check): stock and ETF valuation context
- [moat_watch](/moat_watch): moat-health monitoring and peer-relative competitive-strength tracking
- [harvest_alert](/harvest_alert): tax-loss harvesting scanner with wash-sale checks and replacement suggestions
- [etf_ingest](/etf_ingest): bulk holdings import pipeline
- [etf_catalog](/etf_catalog): ETF universe catalog fetch utilities
- [ingestion_samples](/ingestion_samples): sample raw holdings templates
- [tests](/tests): shared root tests for the original overlap engine

## Data and Ingestion Utilities

This repo also includes utilities for expanding ETF coverage locally.

Fetch the ETF symbol catalog:

```bash
python fetch_etf_catalog.py
```

Bulk-ingest ETF holdings from a normalized CSV:

```bash
python ingest_etf_holdings.py --source-csv ingestion_samples/bulk_holdings_template.csv --target both --pretty
```

These utilities populate the shared overlap/global-exposure datasets used by the dashboard and APIs.

## What Makes This Repo Different

This is not a single script or a single dashboard page. It is a collection of research and investor-education products that share:

- a common local development environment
- a common Streamlit interface
- reusable sample datasets
- standalone package boundaries for each feature
- production-style service layering with APIs, CLIs, and tests

## Notes

- This repository is built to run locally without paid APIs.
- Many features use realistic mock or sample datasets plus provider abstractions for future live integrations.
- Several products surface educational estimates, not personalized tax, legal, or investment advice.
- Some Streamlit imports will emit the usual `missing ScriptRunContext` warning when imported outside `streamlit run`; that is expected in bare import smoke checks.

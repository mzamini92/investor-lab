# Hedgefund Dependency Engine

Hedgefund Dependency Engine is a startup-ready ETF portfolio analytics core that performs:

1. look-through exposure propagation
2. factor / theme loading estimation
3. scenario shock transmission
4. graph / network concentration analysis

It is designed to show what an ETF portfolio really owns, what macro engines it depends on, how shocks transmit through it, and where hidden concentration hubs live.

## Why this is more advanced than ordinary retail tools

Most portfolio tools stop at:

- ETF allocation
- sector charts
- country domicile
- stock overlap lists

This engine goes further by:

- propagating ETF allocations into underlying companies
- mapping companies into revenue geography and macro dependency loadings
- transmitting scenario shocks through dependency weights
- constructing a multi-layer dependency graph and ranking concentration hubs with centrality metrics

## Core algorithms

### 1. Look-Through Exposure Propagation

For ETF `k` with portfolio weight `W_k` and company `i` with ETF holding weight `H_k,i`:

`E_i = Σ_k (W_k * H_k,i)`

Those company exposures are then aggregated into:

- country
- region
- sector
- currency
- market cap
- revenue geography
- macro dependency loadings

### 2. Factor / Theme Loading Estimation

Each company has dependency weights such as:

- `us_consumer`
- `china_demand`
- `europe_demand`
- `ai_capex`
- `cloud_spending`
- `global_semiconductors`
- `industrial_capex`
- `energy_prices`
- `healthcare_spending`
- `financial_conditions`
- `usd_strength`
- `interest_rate_sensitivity`
- `emerging_market_growth`

Portfolio dependency exposure is:

`Dep_d = Σ_i (E_i * b_i,d)`

Revenue geography is also aggregated:

`Rev_r = Σ_i (E_i * revenue_share_i,r)`

### 3. Scenario Shock Transmission Engine

Each scenario defines shock weights over dependency dimensions.

Portfolio impact:

`Impact_s = Σ_d (Dep_d * shock_weight_s,d)`

Company impact:

`CompanyImpact_i,s = E_i * Σ_d (b_i,d * shock_weight_s,d)`

ETF impact is then rolled back up from company contributions.

### 4. Graph / Network Concentration Analysis

The engine builds:

`Portfolio -> ETF -> Company -> Dependency`

and also adds country, region, and currency nodes.

It computes:

- weighted degree
- degree centrality
- betweenness centrality
- eigenvector centrality

to identify concentration hubs and fragile pathways.

## Installation

```bash
cd .
python3 -m venv .venv
source .venv/bin/activate
pip install -r hedgefund_dependency_engine/requirements.txt
```

## Run the CLI

```bash
.venv/bin/python hedgefund_dependency_engine/main.py --portfolio hedgefund_dependency_engine/sample_portfolio.json --pretty
.venv/bin/python hedgefund_dependency_engine/main.py --portfolio hedgefund_dependency_engine/sample_portfolio.json --scenario china_slowdown --scenario ai_boom --save-charts --output-dir ./output
.venv/bin/python hedgefund_dependency_engine/main.py --portfolio hedgefund_dependency_engine/sample_portfolio.json --event war_supply_shock:1.2 --event pandemic_wave --headline "shipping disruption and covid lockdown risk are rising" --pretty
```

## Run the API

```bash
uvicorn hedgefund_dependency_engine.app.api:app --reload
```

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## API endpoints

- `GET /health`
- `GET /supported-etfs`
- `GET /sample-portfolio`
- `GET /sample-scenarios`
- `GET /event-templates`
- `GET /live-news-headlines`
- `GET /live-news-suggestions`
- `GET /sample-graph`
- `GET /sample-dependencies`
- `POST /analyze-portfolio`

`POST /analyze-portfolio` also accepts:

- `scenario_names`
- `dynamic_events` with `name` and `severity`
- `headline_context` for keyword-driven event inference

## Live news ingestion

The engine can fetch current macro headlines from public RSS feeds and turn them into suggested dynamic events.

- live headlines are fetched from public Google News RSS search feeds across macro, geopolitics, health, trade, and technology query groups
- those headlines are matched against curated event templates such as `war_supply_shock`, `pandemic_wave`, and `tariff_escalation`
- the matcher suggests event names, confidence scores, severity hints, and a prebuilt headline context string

This powers:

- `GET /live-news-suggestions`
- the Streamlit hedgefund tab's `Fetch live headlines` action
- CLI-driven event overlays via `--event` and `--headline`

## Sample input

```json
[
  {"ticker": "VTI", "amount": 2000},
  {"ticker": "QQQ", "amount": 1000},
  {"ticker": "VXUS", "amount": 1500},
  {"ticker": "EEM", "amount": 500},
  {"ticker": "ARKK", "amount": 300}
]
```

## What the output includes

- normalized ETF weights
- company exposures
- country, region, sector, currency, and market-cap exposures
- revenue geography exposures
- dependency exposures
- overlap matrix and pairwise redundancy metrics
- HHI and effective counts
- diversification, economic reality gap, and macro dependence scores
- scenario results with top company / ETF / dependency contributors
- graph nodes, edges, and centrality tables
- warnings, insights, and recommendations

## Metrics

### HHI

`HHI = Σ_j p_j^2`

### Effective count

`N_eff = 1 / HHI`

### Economic Reality Gap

A deterministic score comparing:

- apparent diversification from ETF count and label-region mix
- actual concentration in companies, countries, regions, dependencies, and currencies

Higher means the portfolio looks more diversified than it really is.

### Global Diversification Score

A 0-100 score that rewards:

- broader country spread
- broader region spread
- broader revenue spread
- broader dependency spread
- lower currency concentration

and penalizes:

- dominant U.S. exposure
- dominant USD exposure
- dominant single dependency exposure
- low effective counts

### Macro Dependence Score

A 0-100 score where higher means the portfolio is excessively dependent on a small number of economic drivers.

## Data files

- ETF holdings: `hedgefund_dependency_engine/app/data/etf_holdings/`
- company metadata: `hedgefund_dependency_engine/app/data/metadata/company_profiles.csv`
- country mapping: `hedgefund_dependency_engine/app/data/metadata/regions.csv`
- scenarios: `hedgefund_dependency_engine/app/data/scenarios/sample_scenarios.csv`
- dynamic event templates: `hedgefund_dependency_engine/app/data/scenarios/event_templates.csv`

## Data limitations

- holdings are simplified mock datasets for local execution
- company dependency weights are curated plus heuristic, not a licensed fundamentals feed
- scenario outputs are vulnerability scores, not return forecasts
- graph centrality reveals structural concentration, not causal certainty

## Future roadmap

- live ETF ingestion and factor data
- richer country-by-country revenue and supplier exposures
- benchmark-relative dependency analysis
- factor covariance and Monte Carlo simulation
- richer graph clustering and contagion metrics

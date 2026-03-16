# Economic Dependency Heatmap

Economic Dependency Heatmap answers a harder question than ordinary allocation tools:

"What does this portfolio really depend on?"

Instead of stopping at ETF labels, country domicile, or sector weights, this feature looks through ETF holdings and maps the portfolio into:

- company-level exposure
- domicile and revenue geography
- hidden macro drivers such as AI capex, China demand, US consumer exposure, USD strength, and energy prices
- concentration metrics across countries, regions, currencies, revenue buckets, and macro engines
- scenario sensitivities for shocks like China slowdown, Europe recession, AI boom, USD surge, and Fed tightening

## Why it matters

A portfolio can look globally diversified on the surface and still be economically concentrated underneath.

Examples:

- U.S. ETFs plus international ETFs can still be heavily tied to U.S. demand and USD
- non-China ETFs can still rely on China demand through multinationals
- broad equity exposure can still be dominated by AI capex, cloud spending, or semiconductors

This project is designed to make that hidden structure visible.

## How it differs from ordinary portfolio tools

Most tools stop at:

- ETF allocation pie charts
- stock overlap lists
- domicile-based country charts

This project adds:

- revenue geography exposure
- macro dependency scoring
- economic reality gap analysis
- dependency shock scenarios
- heatmap-ready, map-ready, and graph-ready outputs

## Installation

```bash
cd .
python3 -m venv .venv
source .venv/bin/activate
pip install -r economic_dependency_heatmap/requirements.txt
```

## Run the CLI

```bash
.venv/bin/python economic_dependency_heatmap/main.py --portfolio economic_dependency_heatmap/sample_portfolio.json --pretty
.venv/bin/python economic_dependency_heatmap/main.py --portfolio economic_dependency_heatmap/sample_portfolio.json --scenario china_slowdown --scenario ai_boom --save-charts --output-dir ./output
```

## Run the API

```bash
uvicorn economic_dependency_heatmap.app.api:app --reload
```

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## API endpoints

- `GET /health`
- `GET /supported-etfs`
- `GET /sample-portfolio`
- `GET /sample-scenarios`
- `GET /sample-heatmap`
- `GET /sample-map-data`
- `POST /analyze-dependencies`

## Sample input

```json
[
  {"ticker": "VTI", "amount": 2000},
  {"ticker": "VXUS", "amount": 1500},
  {"ticker": "QQQ", "amount": 1000},
  {"ticker": "EEM", "amount": 500}
]
```

## Sample output highlights

- normalized ETF portfolio weights
- underlying company exposures
- country, region, currency, and sector exposure tables
- revenue geography exposure
- macro dependency exposure
- heatmap-ready dependency data
- map-ready global exposure data
- network graph data
- scenario impact results
- diversification scores
- warnings, insights, recommendations, and a viral summary card

## Methodology

### ETF weights

For ETF `k` with amount `A_k`:

`W_k = A_k / ΣA`

### Company exposure

For company `i`:

`E_i = Σ_k (W_k * H_k,i)`

### Revenue geography exposure

For revenue bucket `r`:

`Rev_r = Σ_i (E_i * revenue_share_i,r)`

### Macro dependency exposure

For macro driver `d`:

`Dep_d = Σ_i (E_i * dependency_score_i,d)`

### Scenario impact

For scenario `s`:

`ScenarioImpact_s = Σ_d (Dep_d * ShockWeight_s,d)`

This MVP treats scenario impact as a deterministic sensitivity score, not a forecasted return.

### Economic Reality Gap

The Economic Reality Gap is higher when:

- the portfolio appears diversified by ETF count and label mix
- but actual concentration remains high across macro drivers, regions, or currencies

The implementation combines:

- perceived diversification from ETF count and label-region spread
- divergence between label mix and revenue geography
- realized concentration in macro dependencies, regions, and currencies

### Global Diversification Score

The 0-100 diversification score rewards:

- broader country spread
- broader region spread
- broader revenue geography
- lower dependency concentration
- lower currency concentration

It penalizes:

- dominant U.S. exposure
- dominant USD exposure
- dominant single dependency exposure
- small effective numbers of countries, regions, or macro drivers

### Macro Dependence Score

The Macro Dependence Score is a concentration score for hidden economic engines.
Higher means the portfolio depends on fewer drivers.

## Data files

- ETF holdings: `economic_dependency_heatmap/app/data/etf_holdings/`
- curated company dependency profiles: `economic_dependency_heatmap/app/data/metadata/company_profiles.csv`
- country mapping: `economic_dependency_heatmap/app/data/metadata/regions.csv`
- scenarios: `economic_dependency_heatmap/app/data/scenarios/sample_scenarios.csv`

The provider uses curated metadata where available and falls back to deterministic heuristics for uncovered companies.

## Data limitations

- ETF holdings are simplified mock datasets for local execution
- company macro mappings are heuristic, not vendor fundamentals
- revenue geography is partly curated and partly inferred from the sample holdings metadata
- scenario outputs are sensitivity scores, not predicted P&L

## Future roadmap

- live ETF holdings ingestion
- richer company fundamentals and country-by-country revenue
- factor, duration, and valuation overlays
- benchmark-relative dependency analysis
- interactive frontend storytelling cards and share links

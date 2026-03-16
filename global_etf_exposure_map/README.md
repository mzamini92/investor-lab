# Global ETF Exposure Map

Global ETF Exposure Map helps investors look through ETF labels and quantify their true exposure across countries, regions, sectors, currencies, market-cap tiers, and optional revenue geography.

## Why this matters

Many portfolios that appear globally diversified are still dominated by:

- U.S.-domiciled companies
- North American revenue streams
- USD-linked exposure
- mega-cap developed-market technology firms
- a small number of countries or regions

This tool measures that economic reality directly from underlying ETF holdings.

Current locally supported ETF dataset:

- `VTI`
- `VOO`
- `QQQ`
- `ARKK`
- `VXUS`
- `EEM`
- `IXUS`
- `SCHD`

To add many more ETFs quickly, use the root importer:

```bash
cd /Users/uw-user/Desktop/start
.venv/bin/python ingest_etf_holdings.py --source-csv ingestion_samples/bulk_holdings_template.csv --target both --pretty
```

## What the tool does

- Normalizes ETF portfolio allocations
- Computes underlying company exposure across all ETFs
- Aggregates exposure by country, region, sector, currency, and market-cap tier
- Calculates country and region concentration metrics
- Compares domicile exposure with revenue-based exposure by region
- Scores global diversification with a transparent Global Dependence Score
- Measures the Economic Reality Gap between perceived ETF-label diversification and actual exposure
- Produces map-ready country output for choropleths and dashboard summaries
- Exposes both a CLI and FastAPI interface

## Installation

Python 3.11+ is the intended target. The implementation also remains lightweight enough to run on compatible local Python environments with the listed packages.

```bash
cd /Users/uw-user/Desktop/start
python3 -m venv .venv
source .venv/bin/activate
pip install '.[dev]'
```

## Run the CLI

```bash
.venv/bin/python global_etf_exposure_map/main.py --portfolio global_etf_exposure_map/sample_portfolio.json
.venv/bin/python global_etf_exposure_map/main.py --portfolio global_etf_exposure_map/sample_portfolio.json --output-json results.json --save-charts --output-dir ./output
```

## Run the API

```bash
uvicorn etf_overlap.api:app --reload
```

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Run the Streamlit app

```bash
streamlit run streamlit_app.py
```

## API endpoints

- `GET /health`
- `GET /sample-portfolio`
- `GET /supported-etfs`
- `GET /sample-map-data`
- `POST /analyze-global-exposure`

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

- normalized ETF weights
- underlying company exposure table
- country, region, currency, sector, and market-cap breakdowns
- country and region HHI
- effective number of countries and regions
- revenue geography comparison
- global dependence score
- economic reality gap
- warnings, insights, and recommendations
- choropleth-ready map rows

## Metric notes

### Portfolio ETF weights

For ETF `k` with invested amount `A_k`:

`W_k = A_k / ΣA`

### Underlying company exposure

For company `i`:

`E_i = Σ_k (W_k * H_k,i)`

Where `H_k,i` is the ETF holding weight of company `i` inside ETF `k`.

### Country and region concentration

- `HHI_country = Σ_c (C_c)^2`
- `Effective countries = 1 / HHI_country`
- `HHI_region = Σ_r (R_r)^2`
- `Effective regions = 1 / HHI_region`

### Economic Reality Gap

This metric compares the ETF-label mix the investor sees with actual geographic exposure. The implementation combines:

- label-based vs actual region divergence
- domicile vs revenue divergence
- region concentration concentration penalty

Higher values imply the headline ETF mix is more misleading.

### Global Dependence Score

Score range: `0` to `100`

The score rewards:

- broader country and region diversification
- broader currency mix
- lower single-region dependence
- lower mega-cap concentration

The score penalizes:

- excessive U.S. concentration
- excessive North America concentration
- excessive USD concentration
- concentration in few countries
- mismatch between label diversification and actual underlying exposure

## Data limitations

- Sample ETF holdings are simplified mock datasets, not live fund feeds.
- Revenue geography uses region-level approximations for startup-MVP usability.
- Currency exposure is based on company reporting / operating currency proxies.
- Domicile exposure is not the same as revenue, supply-chain, or regulatory exposure.

## Future extensions

- live ETF holdings providers
- more granular country-by-country revenue datasets
- factor and style exposure overlays
- benchmark comparison
- scenario analysis by macro shock
- frontend dashboard with interactive world map

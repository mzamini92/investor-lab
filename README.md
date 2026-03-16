# ETF Analytics Platform

Production-style Python project for analyzing ETF portfolios with:

- hidden overlap, concentration, and false diversification detection
- global country, region, currency, sector, and revenue-geography exposure mapping
- economic dependency heatmaps, macro-driver concentration, and scenario sensitivity analysis
- single-ticker and ETF valuation context versus history and peers
- quarterly moat-health tracking for competitive advantage monitoring
- FastAPI endpoints, CLI tools, and a Streamlit dashboard

## Features

- Portfolio look-through analysis across ETF holdings
- Company, sector, country, and style exposure aggregation
- ETF-to-ETF overlap matrix with multiple overlap metrics
- Global country, region, currency, market-cap, and revenue exposure mapping
- Economic dependency heatmaps, macro dependency ranking, and shock scenarios
- Valuation context checks for stocks and ETFs versus history, peers, and Treasury yield
- Moat-health tracking across margins, ROIC spread, pricing power, share trends, and management commentary
- Hidden concentration score, diversification score, and redundancy index
- Global Dependence Score and Economic Reality Gap
- Economic Reality Gap, Global Diversification Score, and Macro Dependence Score
- Magnificent 7 exposure tracking
- Rule-based warnings and portfolio improvement suggestions
- FastAPI service and local CLI
- Streamlit dashboard plus Plotly and NetworkX visualization helpers
- Unit tests for core analytics

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install '.[dev]'
python main.py --portfolio sample_portfolio.json --pretty
pytest
uvicorn etf_overlap.api:app --reload
streamlit run streamlit_app.py
```

## API

- `GET /health`
- `GET /sample-portfolio`
- `GET /catalog-etfs`
- `POST /analyze-portfolio`
- `GET /sample-global-portfolio`
- `GET /supported-global-etfs`
- `GET /sample-map-data`
- `POST /analyze-global-exposure`
- `GET /sample-dependency-portfolio`
- `GET /supported-dependency-etfs`
- `GET /sample-scenarios`
- `GET /sample-dependency-heatmap`
- `GET /sample-dependency-map-data`
- `POST /analyze-dependencies`
- `GET /hedgefund-live-news-headlines`
- `GET /hedgefund-live-news-suggestions`

Example request body:

```json
{
  "positions": [
    {"ticker": "VTI", "amount": 2000},
    {"ticker": "VOO", "amount": 1500},
    {"ticker": "QQQ", "amount": 1000},
    {"ticker": "ARKK", "amount": 500}
  ]
}
```

## Data Providers

The project abstracts ETF holdings behind provider interfaces so you can swap in:

- Local CSV holdings files
- Mock providers for tests and development
- Future live ETF holdings APIs

The default app uses CSV files in `data/holdings/`.

Global exposure datasets live in `global_etf_exposure_map/app/data/etf_holdings/`.

Current locally supported ETF dataset:

- `VTI`
- `VOO`
- `QQQ`
- `ARKK`
- `VXUS`
- `EEM`
- `IXUS`
- `SCHD`

## Streamlit

Run:

```bash
streamlit run streamlit_app.py
```

The dashboard has nine tabs:

- `Overlap Detector`: analyzes duplication, concentration, overlap matrix, and warnings
- `Global Exposure Map`: analyzes country, region, currency, market-cap, and revenue exposure with choropleth-ready charts
- `Economic Dependency Heatmap`: analyzes hidden macro drivers, revenue demand centers, dependency scenarios, and a portfolio dependency network
- `Hedgefund Dependency Engine`: adds deeper look-through propagation, factor/theme loading, scenario shock transmission, overlap metrics, and graph centrality concentration analysis
- `EarningsClarity`: turns quarterly earnings calls into a plain-English 5-point summary for long-term holders, with tone shift detection, watch items, evidence snippets, and portfolio-quarter coverage for supported companies
- `True Cost of Investing`: estimates the long-term dollar cost of fees, tax drag, spreads, turnover, advisory fees, cash drag, and other portfolio frictions, with current-vs-optimized comparisons
- `Economic Regime Translator`: turns macro snapshots into a plain-English regime label, scorecard, historical analogs, transition analysis, and portfolio implication summary
- `ValueCheck`: checks whether a stock or ETF looks cheap, fair, or expensive versus its own history and sector or ETF peers, with a plain-English long-term-holder interpretation
- `MoatWatch`: tracks whether competitive advantage signals are strengthening or eroding quarter to quarter, with moat-health colors, trend alerts, and peer-relative context

You can either:

- use the quick picker to choose ETFs and amounts, with each selected ETF defaulting to `1000`
- upload a portfolio JSON file
- paste a portfolio JSON array manually

For the dependency tabs, you can also filter the scenario set before running the analysis.
The hedgefund tab also supports dynamic event overlays like war, pandemic, tariff escalation, and shipping disruption, plus free-text headline context that auto-matches event templates by keyword.
It now includes live-news ingestion, auto-refresh controls, and a `Top 5 Live Risks Today` card strip driven by current headlines.
The `EarningsClarity` tab supports both single-company review and portfolio-quarter review, plus holdings JSON upload for the supported sample companies.
The `True Cost of Investing` tab supports current-portfolio analysis, side-by-side comparison against a lower-cost alternative, assumptions uploads, downloadable chart exports, and long-horizon wealth-loss visuals.
The `Economic Regime Translator` tab supports current-snapshot classification, prior-snapshot comparison, historical analog matching, and exportable macro regime summaries.
The `ValueCheck` tab supports ticker-level valuation checks, verdict cards, own-history percentile views, peer comparison charts, and markdown/JSON exports.
The `MoatWatch` tab supports single-company moat analysis, watchlist-quarter digests, moat score history, signal radar charts, peer comparison, and alert/watch-item summaries.

Then click analyze and review the charts, tables, warnings, recommendations, summary cards, and downloadable HTML chart exports.

## Bulk ETF Import

You can import many more ETFs from a standardized raw holdings CSV and generate both local datasets automatically:

```bash
python ingest_etf_holdings.py --source-csv ingestion_samples/bulk_holdings_template.csv --target both --pretty
```

This will create:

- overlap holdings files in `data/holdings/`
- global exposure holdings files in `global_etf_exposure_map/app/data/etf_holdings/`

Expected raw CSV columns:

- required: `etf_ticker`, `underlying_ticker`, `company_name`, `holding_weight`, `sector`
- optional but recommended: `country_domicile`, `country_code`, `region`, `currency`, `market_cap`, `market_cap_bucket`, `style_box`, `label_region`, `label_focus`
- optional revenue fields: `revenue_north_america`, `revenue_europe`, `revenue_asia_pacific`, `revenue_emerging_markets`, `revenue_latin_america`, `revenue_middle_east_africa`

If region, currency, or country code are missing, the importer will infer them from `global_etf_exposure_map/app/data/metadata/regions.csv` when possible.

## ETF Catalog Fetch

There is no single free official source that gives both every ETF ticker and every ETF's full holdings in one easy public file. For the ticker universe, this project now uses Nasdaq Trader's official symbol-directory files, which include an `ETF` flag for listed symbols:

- [Nasdaq Trader home](https://www.nasdaqtrader.com/HomePage.aspx)
- [Nasdaq daily list file specification](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/dlcompletespec.pdf)

Fetch the ETF catalog with:

```bash
python fetch_etf_catalog.py
```

This writes:

`data/catalog/us_etf_catalog.csv`

Important:

- this catalog gives you ETF tickers and names
- it does not give you ETF holdings
- for analysis, the ETF must still have holdings data locally, either from the bundled dataset or from `ingest_etf_holdings.py`

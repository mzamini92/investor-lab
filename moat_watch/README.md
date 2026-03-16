# MoatWatch

MoatWatch tracks whether the companies you own are strengthening or losing their competitive advantages over time.

It turns quarterly operating signals into a clear moat-health readout:

- `Strong Green`
- `Green`
- `Yellow`
- `Orange`
- `Red`

## Why this matters

Many long-term investors buy a business because they believe it has durable pricing power, scale, brand strength, switching costs, or innovation leadership.

The problem is that moat erosion is often gradual. It shows up first in signals like:

- gross margin compression
- weaker pricing power
- narrowing ROIC spreads
- slowing market share trends
- softer management commentary around competition or promotions

MoatWatch is designed to make those changes visible before they become obvious in a broken thesis.

## What the score uses

MoatWatch combines these signals into a deterministic moat score:

- gross margin trajectory
- ROIC versus WACC spread
- pricing power proxies
- market share trend
- reinvestment and innovation intensity
- sales efficiency
- commentary-based competitive pressure

## Score construction

Component weights:

- gross margin trajectory: `20%`
- ROIC spread: `20%`
- pricing power: `18%`
- market share: `15%`
- innovation / reinvestment: `12%`
- sales efficiency: `8%`
- commentary pressure: `7%`

Label mapping:

- `< 35`: `Red`
- `< 50`: `Orange`
- `< 65`: `Yellow`
- `< 80`: `Green`
- `>= 80`: `Strong Green`

## Included sample companies

- `SBUX`
- `AAPL`
- `MSFT`
- `NFLX`
- `COST`

Peer datasets are also bundled for:

- `CMG`, `MCD`
- `GOOGL`, `META`, `ORCL`, `CRM`
- `DIS`, `WMT`, `TGT`

## Installation

```bash
cd .
python -m venv .venv
source .venv/bin/activate
pip install -r moat_watch/requirements.txt
```

## Run the CLI

```bash
python moat_watch/main.py analyze --ticker SBUX --quarter 2025Q2 --pretty
python moat_watch/main.py analyze-watchlist --watchlist moat_watch/app/data/watchlists/sample_watchlist.json --quarter 2025Q2 --pretty
```

Optional flags:

- `--output-json result.json`
- `--output-md summary.md`
- `--output-dir ./output`
- `--save-charts`

## Run the API

```bash
uvicorn moat_watch.app.api:app --reload
```

Endpoints:

- `GET /health`
- `GET /sample-watchlist`
- `GET /sample-companies`
- `GET /sample-result/{ticker}`
- `GET /peer-comparison/{ticker}`
- `POST /analyze-company-moat`
- `POST /analyze-watchlist-quarter`

## Sample output concepts

```text
Moat health: Yellow
Why:
- gross margin compressed again
- ROIC spread narrowed
- management tone turned more promotional
- peer comparison looks weaker than a year ago
```

## Limitations

- bundled data is sample data, not live filings or earnings APIs
- market-share and pricing-power inputs are proxies, not perfect ground truth
- commentary detection is intentionally lightweight and rule-based
- this is not a buy/sell engine or return forecast tool

## Extending to real data later

The provider layer is designed so you can plug in:

- SEC filing parsers
- earnings-call transcript pipelines
- alternative market-share datasets
- broker-connected watchlists
- internal quarterly KPI stores

Main extension points:

- `moat_watch/app/providers/base.py`
- `moat_watch/app/providers/moat_provider.py`

## Testing

```bash
pytest moat_watch/tests
```

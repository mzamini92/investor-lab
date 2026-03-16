# ValueCheck

ValueCheck gives a retail investor a fast valuation context check before adding money to a stock or ETF.

Instead of only showing price action, it shows where a ticker trades across multiple valuation metrics versus:

- its own history
- sector or ETF peers
- Treasury yield context for free cash flow

Then it translates that into a plain-English verdict such as `cheap`, `fair`, `slightly expensive`, or `extremely expensive`.

## Why this matters

Many investors know the story around a stock but not the price already embedded in that story.

ValueCheck is built to answer questions like:

- Is this expensive relative to its own history?
- Is it rich relative to peers?
- Does the current multiple imply unusually strong growth assumptions?
- Is this stretched enough that a steady DCA investor should be more patient than usual?

This is not a price target tool or a buy/sell engine. It is valuation context for long-term investors.

## What it covers

- `P/E`
- `EV/EBITDA`
- `P/S`
- `P/B`
- `FCF Yield`
- `FCF Yield - Treasury Yield`
- own-history percentile ranks
- peer median premium or discount
- composite valuation verdict
- implied expectations heuristic
- long-term-holder interpretation

## Included sample universe

Stocks:

- `AAPL`
- `MSFT`
- `NVDA`
- `AMZN`
- `GOOGL`
- `META`
- `JPM`
- `XOM`
- `SNOW`

ETFs:

- `VOO`
- `QQQ`

Additional bundled peer helpers:

- `BAC`
- `WFC`
- `CVX`
- `SPY`
- `IVV`
- `VUG`

## Installation

```bash
cd /Users/uw-user/Desktop/start
python -m venv .venv
source .venv/bin/activate
pip install -r value_check/requirements.txt
```

## Run the CLI

```bash
python value_check/main.py check --ticker MSFT --lookback 10 --treasury-yield 0.042 --pretty
python value_check/main.py check --ticker VOO --asset-type etf --save-charts --output-dir ./output
```

Optional flags:

- `--output-json result.json`
- `--output-md summary.md`
- `--output-dir ./output`
- `--save-charts`

## Run the API

```bash
uvicorn value_check.app.api:app --reload
```

Endpoints:

- `GET /health`
- `GET /supported-tickers`
- `GET /sample-tickers`
- `GET /sample-result/{ticker}`
- `GET /peer-group/{ticker}`
- `POST /value-check`

## Example request

```json
{
  "ticker": "NVDA",
  "lookback_years": 10,
  "treasury_yield": 0.042
}
```

## Example output concepts

- `P/E: 36.2x vs 10-year avg 27.4x`
- `FCF yield: 2.1% vs Treasury yield 4.2%`
- `Peer median P/E: 31.4x`
- `Verdict: slightly expensive`
- `Interpretation: expectations are elevated, but not necessarily at a bubble extreme`

## How the verdict works

The composite score is deterministic and combines:

- own-history percentile ranks
- peer premiums or discounts
- Treasury-relative free-cash-flow context
- metric completeness and confidence

General direction rules:

- higher `P/E`, `EV/EBITDA`, `P/S`, and `P/B` percentile means more expensive
- lower `FCF Yield` percentile means more expensive
- a lower `FCF Yield` than the 10-year Treasury is treated as richer valuation context

Score bands:

- `< 15`: `cheap`
- `< 35`: `slightly cheap`
- `< 55`: `fair`
- `< 72`: `slightly expensive`
- `< 87`: `expensive`
- `>= 87`: `extremely expensive`

## ETF handling

ETF valuation support is included, but with caveats.

ETF metrics use weighted-average holdings proxies where available, not issuer fundamentals. ValueCheck surfaces those limitations clearly in the output so the user understands the difference.

## Limitations

- bundled data is mocked but realistic, not live market data
- history series are simplified valuation snapshots rather than a complete daily dataset
- the implied growth section is a heuristic, not a full DCF
- bank and insurance valuation interpretation needs extra care
- ETF metrics are necessarily more approximate than single-stock fundamentals

## Extending to real providers later

The provider layer is designed so you can replace bundled data with:

- Financial Modeling Prep
- Alpha Vantage
- Polygon
- internal market-data pipelines
- custom valuation and peer datasets

The main extension points live in:

- `/Users/uw-user/Desktop/start/value_check/app/providers/base.py`
- `/Users/uw-user/Desktop/start/value_check/app/providers/valuation_provider.py`

## Testing

```bash
pytest /Users/uw-user/Desktop/start/value_check/tests
```

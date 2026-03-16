# GlobalGap

GlobalGap helps investors quantify home-country bias by comparing a portfolio's US exposure with international valuation, earnings-growth, and dollar-cycle conditions.

It answers questions like:

- How US-heavy is my portfolio?
- How cheap or expensive are international equities versus US equities?
- Where is the dollar in its cycle?
- What happened historically when this valuation gap was this wide?
- What might a modest international allocation do for diversification?

## What It Does

- Computes portfolio US and international equity exposure
- Measures the US versus international valuation gap
- Compares earnings-growth expectations
- Classifies the current dollar cycle regime
- Finds historical analog periods with similar valuation spreads
- Simulates current versus more diversified portfolio mixes
- Produces a plain-English recommendation for long-term investors
- Exposes both a CLI and FastAPI API
- Ships with Plotly visualization helpers and sample datasets

## Installation

```bash
cd /Users/uw-user/Desktop/start
python -m venv .venv
source .venv/bin/activate
pip install -r globalgap/requirements.txt
```

## CLI

```bash
python globalgap/main.py analyze --portfolio globalgap/sample_portfolio.json --pretty
python globalgap/main.py analyze --portfolio globalgap/sample_portfolio.json --save-charts --output-dir ./output/globalgap
```

## API

```bash
uvicorn globalgap.app.api:app --reload
```

Endpoints:

- `GET /health`
- `GET /sample-portfolio`
- `GET /macro-data`
- `GET /valuation-gap`
- `GET /dollar-cycle`
- `POST /analyze-portfolio`

## Sample Input

```json
[
  {"ticker": "VTI", "quantity": 120, "price": 285.0},
  {"ticker": "QQQ", "quantity": 20, "price": 515.0},
  {"ticker": "AAPL", "quantity": 10, "price": 214.0}
]
```

## Example Output Themes

- `Portfolio Exposure`: 90%+ US home bias if the portfolio is mostly VTI, QQQ, and US single-name stocks
- `Valuation Gap`: international equities may trade at a meaningful discount to US equities
- `Dollar Cycle`: a weakening or peak dollar historically improved the case for international diversification
- `Historical Analog`: periods like 1985, 2000, or 2007 can be surfaced when valuation spreads were similarly wide
- `Recommendation`: a modest non-US allocation may reduce concentration risk and improve diversification

## Methodology

### Portfolio Geography

Each supported ticker is mapped to a US exposure percentage and international exposure percentage.

Portfolio US weight is computed as:

`portfolio_US_weight = Σ(position_weight * ticker_US_exposure)`

### Valuation Gap

The core spread is:

`valuation_spread = US_forward_PE / International_forward_PE`

Higher spread means the US trades at a larger premium.

### Dollar Cycle

The dollar regime uses:

- DXY level
- percentile versus recent history
- directional trend

### Historical Analogs

The analog engine finds prior periods where the valuation spread was similarly wide or wider, then reads the following 5-year international minus US relative outcome from the sample history.

### Simulation

The simulation compares:

- current US/international mix
- a more diversified mix

using sample historical return correlations for US and international equities.

## Data Limitations

- The repository uses bundled sample datasets so it runs fully offline.
- Valuation, earnings, and dollar-cycle inputs are research-style proxies, not live market feeds.
- Historical analog analysis is illustrative and should not be treated as a forecast.
- This is a macro clarity tool, not investment advice.

## Future Extensions

- Live FRED and market-data adapters
- ETF holdings-aware geographic look-through
- Region-level valuation splits beyond simple US vs international
- More detailed currency and hedging analysis
- Richer shared-dashboard comparisons against the investor's full ETF analytics stack

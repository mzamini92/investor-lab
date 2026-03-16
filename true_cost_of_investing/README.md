# True Cost of Investing Calculator

True Cost of Investing Calculator shows how seemingly small investing frictions compound into large wealth losses over long horizons.

## What it does

This tool estimates the long-term cost of:

- expense ratios
- advisory fees
- dividend tax drag
- turnover-driven tax drag
- bid-ask spreads and slippage
- rebalancing friction
- commissions
- foreign withholding drag
- fund layering
- cash drag

It projects the difference between:

- gross wealth with no frictions
- net wealth after all modeled frictions
- the compounded ending-value hit from each friction source

The result is designed to answer:

“What am I really losing over 30 years?”

## Why this matters

Most investors focus on one visible number like a fund expense ratio. In practice, hidden taxes, advisory fees, turnover, and trading friction can matter just as much or more. A drag that looks small in one year can translate into very large lost wealth over decades of compounding.

## What costs are included

- fund expense ratios
- layered fund fees
- advisory fees
- dividend taxes in taxable accounts
- turnover-driven capital gains drag
- foreign withholding tax assumptions
- spread and slippage assumptions
- rebalancing friction
- commissions
- cash drag

## What assumptions are estimated

This is an estimation engine, not a tax filing engine. Some costs are modeled heuristically, especially:

- turnover tax realization
- rebalancing trade size
- spread/slippage frequency
- cash drag

These assumptions are transparent in the code and sample files and can be adjusted.

## Installation

```bash
cd .
python3 -m venv .venv
source .venv/bin/activate
pip install -r true_cost_of_investing/requirements.txt
```

## Run the API

```bash
uvicorn true_cost_of_investing.app.api:app --reload
```

Available endpoints:

- `GET /health`
- `GET /sample-portfolio`
- `GET /sample-assumptions`
- `GET /sample-result`
- `POST /analyze-portfolio-cost`
- `POST /compare-portfolios`

## Run the CLI

Analyze one portfolio:

```bash
python true_cost_of_investing/main.py analyze \
  --portfolio true_cost_of_investing/app/data/portfolios/sample_high_fee_portfolio.json \
  --assumptions true_cost_of_investing/app/data/assumptions/taxable_account.json \
  --pretty
```

Compare current vs optimized:

```bash
python true_cost_of_investing/main.py compare \
  --current true_cost_of_investing/app/data/portfolios/sample_high_fee_portfolio.json \
  --alternative true_cost_of_investing/app/data/portfolios/sample_low_cost_portfolio.json \
  --assumptions true_cost_of_investing/app/data/assumptions/taxable_account.json \
  --pretty
```

Optional flags:

- `--output-json result.json`
- `--output-md summary.md`
- `--output-dir ./output`
- `--save-charts`

## Sample input

```json
[
  {
    "ticker": "VOO",
    "amount": 12000,
    "expense_ratio": 0.0003,
    "asset_type": "ETF",
    "qualified_dividend_yield": 0.015
  },
  {
    "ticker": "QQQ",
    "amount": 5000,
    "expense_ratio": 0.0020,
    "asset_type": "ETF",
    "qualified_dividend_yield": 0.006
  }
]
```

## Sample output themes

- total hidden annual drag rate
- annual friction breakdown by category
- ending value gross vs net
- lifetime dollars lost
- biggest cost category
- recommendations to reduce friction
- current vs optimized comparison

## Methodology

### Holding weights

`w_i = amount_i / total_portfolio_value`

### Blended expense ratio

`ER_portfolio = Σ(w_i * expense_ratio_i)`

### Dividend tax drag

For taxable accounts:

`DividendTaxDrag = Σ(position_value_i * (qualified_yield_i * qualified_tax_rate + nonqualified_yield_i * ordinary_tax_rate))`

### Turnover tax drag

The model uses a transparent heuristic:

`TurnoverTaxDrag = position_value * turnover_rate * assumed_realized_gain_ratio * capital_gains_tax_rate`

The default assumed realized gain ratio is intentionally simple and configurable.

### Trading friction

Spread, slippage, rebalancing, and commissions are estimated from basis-point assumptions and trading frequency proxies.

### Projection engine

The engine compounds monthly and applies friction categories as recurring drags to the evolving portfolio balance while also adding monthly contributions.

### Opportunity cost by category

Each friction category’s ending-value impact is estimated by rerunning the projection with that category removed and measuring the difference in ending wealth.

## Limitations and disclaimers

- This is an estimation engine, not tax advice.
- It does not replace brokerage statements, advisor disclosures, or tax preparation.
- Real tax outcomes depend on basis, holding period, distributions, and jurisdiction-specific rules.
- Trading friction varies by market conditions and order quality.

## Future extensions

- live brokerage import
- live ETF metadata feeds
- multi-account household views
- tax-location optimization workflows
- state-specific tax presets
- retirement withdrawal modeling

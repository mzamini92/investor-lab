# HarvestAlert

HarvestAlert scans taxable brokerage data for tax-loss harvesting opportunities and suggests a similar replacement ETF so the investor can keep roughly the same strategy in place.

## What it does

- finds taxable positions or lots currently at a loss
- estimates whether the loss is large enough to matter after trading friction
- applies a configurable tax-rate assumption
- screens for likely wash-sale conflicts
- recommends similar replacement ETFs
- ranks opportunities by net benefit, wash-sale risk, and strategy preservation

## Why this matters

Tax-loss harvesting is one of the few repeatable tax-aware portfolio habits that can improve after-tax outcomes without changing the investor’s long-term plan much.

The friction is operational:

- Which lot should you sell?
- Is the loss big enough to be worth it?
- What can you buy instead?
- Will a recent or recurring buy create a wash-sale problem?

HarvestAlert turns those questions into a clearer workflow.

## How the scan works

1. Normalize accounts, positions, lots, and transactions
2. Find unrealized losses in taxable accounts
3. Estimate tax savings and trading costs
4. Screen recent and scheduled purchases for wash-sale risk
5. Rank replacement ETFs by similarity and drift
6. Return ranked opportunities and plain-English alerts

## What wash-sale screening covers

HarvestAlert checks for:

- same-ticker buys within 30 days before the proposed harvest date
- recent buys in taxable accounts
- recent buys in IRA or Roth IRA accounts
- recurring-buy or scheduled-buy flags if included in the transaction history
- explicitly prohibited replacement pairs in the bundled replacement universe

## What it does not guarantee

- It does not determine every substantially-identical edge case perfectly
- It does not replace tax advice
- It depends on the completeness of the account and transaction data you supply

## Included sample scenarios

- clear harvest opportunity with safe replacement: `VEA -> IEFA`
- safe broad-market replacement example: `VXF -> SCHA`
- too-small loss example: `VXUS`
- IRA wash-sale conflict example: `QQQ`
- no clean replacement example: `ARKK`
- mixed-gain / mixed-loss lot examples

## Installation

```bash
cd .
python -m venv .venv
source .venv/bin/activate
pip install -r harvest_alert/requirements.txt
```

## Run the CLI

```bash
python harvest_alert/main.py scan \
  --accounts harvest_alert/app/data/accounts/accounts.json \
  --positions harvest_alert/app/data/positions/positions.json \
  --lots harvest_alert/app/data/positions/lots.json \
  --transactions harvest_alert/app/data/transactions/transactions.json \
  --tax-assumptions harvest_alert/app/data/sample/tax_assumptions.json \
  --replacements harvest_alert/app/data/replacements/replacements.json \
  --pretty
```

Single-position shortcut:

```bash
python harvest_alert/main.py evaluate --ticker VEA --account taxable_main --pretty
```

## Run the API

```bash
uvicorn harvest_alert.app.api:app --reload
```

Endpoints:

- `GET /health`
- `GET /sample-accounts`
- `GET /sample-positions`
- `GET /sample-replacements`
- `GET /sample-result`
- `POST /scan-harvest-opportunities`
- `POST /evaluate-single-position`

## Example output

```text
VEA is down about $920 from cost basis in taxable_main.
Selling it and holding IEFA for 31 days could create an estimated tax benefit of about $258 with low expected exposure drift.
Wash-sale screen: none detected.
```

## Assumptions and disclaimers

- This tool provides educational estimates, not tax advice.
- Wash-sale rules can be fact-specific.
- Users should confirm with a tax professional when necessary.
- Data completeness matters, especially across multiple accounts.

## Extending to real brokerage integrations later

The provider layer is designed so you can swap in:

- Plaid investment account data
- direct brokerage APIs
- custodial exports
- recurring-investment plan feeds
- tax-lot systems from portfolio accounting tools

Main extension points:

- `harvest_alert/app/providers/base.py`
- `harvest_alert/app/providers/brokerage_provider.py`

## Testing

```bash
pytest harvest_alert/tests
```

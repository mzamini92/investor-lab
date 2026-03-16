# Economic Regime Translator

Economic Regime Translator converts macro data into a plain-English economic regime label, confidence score, historical analogs, and portfolio implication summary.

## What it does

The tool ingests a macro snapshot with inputs such as:

- Fed policy rate and recent change
- inflation levels and recent trend
- unemployment and labor trend
- ISM / PMI-style growth signals
- yield curve shape
- credit spreads
- earnings revision breadth and momentum

It then produces:

- a current regime label
- explanation of the main drivers
- sub-scores for growth, inflation, policy, credit, earnings, curve warning, and recession risk
- top historical analog periods
- plain-English portfolio implications
- transition analysis versus a prior snapshot

## Why it matters

Retail investors hear phrases like “soft landing” or “late cycle” without a clear framework for deciding what the data actually says. This project turns disconnected macro prints into one coherent regime readout with explainable rules.

## How the model works

### 1. Indicator normalization

The engine converts raw inputs into interpretable states such as:

- inflation cooling / sticky / reheating
- labor tightening / stable / loosening
- curve flat / inverted / steep
- credit benign / caution / stressed
- earnings improving / mixed / deteriorating

### 2. Scorecard engine

Deterministic sub-scores are built for:

- growth
- inflation
- policy restrictiveness
- credit stress
- earnings momentum
- curve warning
- recession risk
- risk appetite

### 3. Rule-based regime classifier

The scorecard and indicator states feed a transparent rules engine that maps the environment into labels such as:

- Disinflationary soft landing
- Late-cycle slowdown
- Growth scare under restrictive policy
- Credit stress regime
- Stagflation risk regime

### 4. Historical analog engine

The current snapshot is compared against a historical dataset using normalized indicator vectors and distance-based similarity.

## Installation

```bash
cd .
python3 -m venv .venv
source .venv/bin/activate
pip install -r economic_regime_translator/requirements.txt
```

## Run the API

```bash
uvicorn economic_regime_translator.app.api:app --reload
```

Endpoints:

- `GET /health`
- `GET /sample-current-snapshot`
- `GET /sample-history`
- `GET /sample-result`
- `POST /classify-regime`
- `POST /compare-snapshots`

## Run the CLI

Classify a snapshot:

```bash
python economic_regime_translator/main.py classify \
  --snapshot economic_regime_translator/app/data/samples/current_snapshot.json \
  --history economic_regime_translator/app/data/historical/historical_macro.csv \
  --with-analogs \
  --pretty
```

Compare current vs prior:

```bash
python economic_regime_translator/main.py compare \
  --current economic_regime_translator/app/data/samples/current_snapshot.json \
  --prior economic_regime_translator/app/data/samples/prior_snapshot.json \
  --history economic_regime_translator/app/data/historical/historical_macro.csv \
  --pretty
```

Optional flags:

- `--output-json result.json`
- `--output-md summary.md`
- `--with-analogs`

## Sample output themes

- Current regime: `Disinflationary soft landing`
- Confidence score
- Historical precedent note
- What changed since the prior snapshot
- Watch items for long-term investors

## Limitations and disclaimers

- This is a macro interpretation tool, not a market-timing signal.
- Historical analogs are simplified and sample-data-driven in this MVP.
- Real-world macro regimes are fuzzy, overlapping, and often revised later.
- Asset behavior examples are descriptive, not predictive.

## Integrating real data later

The provider layer is designed so you can swap in:

- FRED series adapters
- Treasury curve feeds
- credit spread datasets
- earnings revision feeds
- financial conditions indexes

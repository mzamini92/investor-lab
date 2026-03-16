# EarningsClarity

EarningsClarity turns long earnings transcripts into plain-English, long-term-holder-focused summaries.

## Who it is for

- long-term investors
- buy-and-hold investors
- steady DCA investors
- anyone who wants to know what actually changed after earnings without reading 40 pages of transcript

## Why this is different from generic transcript summaries

EarningsClarity is not a hype summary or trader note. It is designed to answer:

- what management actually said
- what changed versus last quarter
- what matters for a long-term holder
- whether the tone was truly good, mixed, or more cautious than the headline beat implies

## Core workflow

1. load transcript and prior-quarter transcript
2. parse speakers and sections
3. compute beat/miss versus estimates
4. detect guidance and caution language
5. extract major themes and compare tone versus the prior quarter
6. generate a 5-point plain-English summary for a long-term holder

## Heuristic methodology

The MVP is deterministic and transparent:

- repeated cautious qualifiers raise the guidance caution score
- phrases like `lowered outlook`, `visibility is limited`, and `margin pressure` carry extra weight
- strong headline beats do not dominate the summary if guidance and tone turn more cautious
- analyst Q&A defensiveness can increase the concern score
- confidence rises when multiple independent evidence snippets support the same conclusion

## Install

```bash
cd /Users/uw-user/Desktop/start
python3 -m venv .venv
source .venv/bin/activate
pip install -r earnings_clarity/requirements.txt
```

## Run the API

```bash
uvicorn earnings_clarity.app.api:app --reload
```

Endpoints:

- `GET /health`
- `GET /sample-holdings`
- `GET /sample-companies`
- `GET /sample-earnings-events`
- `POST /analyze-earnings-call`
- `POST /analyze-portfolio-quarter`
- `GET /sample-summary/{ticker}`

## Run the CLI

Analyze one call:

```bash
python earnings_clarity/main.py analyze-call \
  --ticker AAPL \
  --quarter 2025Q4 \
  --transcript earnings_clarity/app/data/transcripts/AAPL_2025Q4.txt \
  --prior earnings_clarity/app/data/transcripts/AAPL_2025Q3.txt
```

Analyze a holdings file for one quarter:

```bash
python earnings_clarity/main.py analyze-portfolio \
  --holdings earnings_clarity/app/data/holdings/sample_holdings.json \
  --quarter 2025Q4
```

## Sample output shape

- headline result vs expectations
- guidance view
- key risk flag
- tone shift versus prior quarter
- long-term takeaway
- thesis status
- confidence score
- evidence snippets
- detected topics
- watch items
- 5-point summary

## Data files

- transcripts: `earnings_clarity/app/data/transcripts/`
- earnings metadata: `earnings_clarity/app/data/earnings/`
- holdings: `earnings_clarity/app/data/holdings/`

## Limitations

- sample transcripts are synthetic but realistic
- heuristics are transparent and testable, but not equivalent to a full analyst research desk
- no buy/sell calls and no short-term trading guidance
- transcript parsing assumes a reasonably standard speaker-label format

## Extending with real providers later

The provider interfaces are already split so you can plug in:

- transcript APIs
- SEC filing adapters
- earnings calendar providers
- brokerage-linked holdings
- notification or email workflows

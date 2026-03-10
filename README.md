# Monday.com Business Intelligence Agent

An AI-powered BI agent that answers founder-level business questions from Monday.com data using natural language.

## Architecture Overview

```
app.py                  ← Streamlit UI (chat + dashboard + raw data)
├── monday_client.py    ← Monday.com GraphQL API client + data processor
├── analyzer.py         ← Business intelligence computation engine
└── agent.py            ← Groq LLM agent with function-calling loop
```

### How it works

1. **monday_client.py**: Connects to Monday.com's GraphQL API, paginates through all items on both boards, and normalizes raw data (dates, numbers, statuses, JSON column values).

2. **analyzer.py**: Pure Python analytics — pipeline overview, sector breakdown, quarterly pipeline, win/loss analysis, operational health, cross-board sector 360 views.

3. **agent.py**: Uses Groq's LLaMA 3.3 70B to interpret natural language queries. The LLM decides which analysis function to call, receives the result, then writes a founder-friendly narrative.

4. **app.py**: Streamlit interface with Chat tab, Dashboard tab (live metrics), and Raw Data tab.

## Setup

### Prerequisites
- Python 3.9+
- Monday.com account with two boards: Deals and Work Orders
- Groq API key (free at console.groq.com)

### Install

```bash
pip install -r requirements.txt
```

### Run locally

```bash
streamlit run app.py
```

### Deploy to Streamlit Cloud

1. Push this folder to a GitHub repo
2. Go to share.streamlit.io
3. Connect your repo and set `app.py` as the entry point
4. No secrets needed — credentials are entered in-app

## Monday.com Board Setup

Import the provided CSVs into Monday.com:

**Deals board** — recommended columns:
- Name (default)
- Deal Value (numbers)
- Stage/Status (status)
- Sector/Industry (text or dropdown)
- Close Date (date)
- Account Manager/Owner (person or text)
- Company (text)

**Work Orders board** — recommended columns:
- Name (default)
- Contract Value (numbers)
- Status (status)
- Sector (text or dropdown)
- Due Date (date)
- Assigned To (person or text)

The agent auto-detects column mappings by keyword matching — you don't need exact column names.

## Environment Variables (optional)

If you prefer not to enter credentials in the UI, set:

```bash
MONDAY_API_TOKEN=your_token
GROQ_API_KEY=your_key
DEALS_BOARD_ID=your_board_id
WO_BOARD_ID=your_board_id
```

## Notes on Data Quality

The agent handles:
- Missing/null values (reports percentages, skips gracefully)
- Inconsistent date formats (tries 8 common formats)
- JSON-encoded column values (Monday.com stores some values as JSON)
- Mixed number formats (commas, currency symbols, etc.)
- Status columns stored as JSON labels

Data quality issues are surfaced in both the Dashboard tab and in agent responses.

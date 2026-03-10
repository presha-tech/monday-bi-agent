# Decision Log — Monday.com BI Agent

## Key Assumptions

**Data & boards:**  
I assumed the two Monday.com boards follow conventional naming — "Deals" for sales pipeline and "Work Orders" for project execution. Rather than hardcoding column names, I built an auto-detection layer that maps columns by keyword matching (e.g. any column containing "revenue", "value", "amount" maps to the `value` concept). This handles the real-world reality that column names vary by how the CSV was imported.

**Data quality:**  
Real Monday.com data is messy. I assumed: (a) date fields may appear in multiple formats; (b) numeric fields may contain currency symbols or commas; (c) status fields are often stored as JSON label objects; (d) some records will have missing values for key fields. The agent communicates data quality caveats in its responses rather than silently dropping records.

**User persona:**  
Founders and execs want insights, not raw numbers. I designed the LLM prompt to always provide a "so what" — context, implications, caveats — not just a data dump.

---

## Trade-offs

**Groq (LLaMA 3.3 70B) over OpenAI GPT-4:**  
Groq offers dramatically faster inference (100-300 tok/s vs ~30 for GPT-4), which makes the chat feel more responsive. LLaMA 3.3 70B is strong enough for structured function-calling and business narrative. Trade-off: slightly less reliable JSON formatting, mitigated by robust extraction with regex fallbacks.

**Custom function-calling loop over OpenAI tool_use API:**  
Groq doesn't support native tool_use in the same format. I implemented a text-based function call pattern (the LLM returns `{"function": "...", "args": {...}}`) with a Python router. This is less elegant than native tool calling but works reliably with Groq's API and gives full control over the loop.

**In-memory analytics (no database) over a SQL layer:**  
All analysis runs in Python at query time. For hundreds to low thousands of records (typical for Monday.com boards), this is fast enough and removes infrastructure complexity. Trade-off: doesn't scale to tens of thousands of records. With more time, I'd add a DuckDB layer for complex multi-dimensional queries.

**Column auto-detection over config file:**  
Rather than asking users to map their column names upfront, I infer mappings by keyword. This makes onboarding instant. Trade-off: occasionally misidentifies a column. I surface the detected mapping in the Raw Data → Column Mapping tab so users can verify.

---

## What I'd Do With More Time

1. **Persistent config** — Store board IDs and API keys in Streamlit secrets or a config file so users don't re-enter on each session.
2. **Chart visualizations** — Add Plotly charts for pipeline funnel, sector distribution bar charts, quarterly trends.
3. **Multi-turn memory** — The current conversation history grows unbounded. I'd add a sliding window + summary to handle long sessions.
4. **Webhook / live refresh** — Poll or subscribe to Monday.com webhooks so data auto-refreshes when boards change.
5. **Export** — Let users download the leadership brief as a PDF or copy it to clipboard.

---

## Interpretation of "Leadership Updates"

I interpreted this as a **structured executive briefing** that a founder could paste into a board meeting deck or Slack. The "Generate Leadership Brief" button triggers a prompt asking the agent to write a narrative covering: pipeline health, current quarter outlook, top deals to watch, operational risk (overdue work orders), and data quality caveats. The output is conversational but structured — designed to be read in 60 seconds by a time-pressed executive.

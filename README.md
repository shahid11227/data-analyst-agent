# Data Analyst Agent

An AI agent that profiles a dataset, writes SQL, runs custom Python analysis,
and draws charts -- all from natural-language questions in a chat interface.

## How it works

1. You upload a CSV in the Streamlit app.
2. The data loads into a pandas DataFrame and is registered as a table in an
   in-memory DuckDB database.
3. A LangChain agent (`create_agent`, LangChain v1) reads your question and
   picks one of three tools:
   - `eda_summary` -- shape, dtypes, missing values, descriptive statistics
   - `run_sql` -- DuckDB SQL against the dataset
   - `run_python` -- pandas/matplotlib for anything SQL can't express (custom
     calculations, multi-step logic, charts)
4. The LLM is Llama 3.3 70B served for free via Groq -- no local GPU, no paid
   API key.
5. The agent's answer, and any chart it drew, render back in the chat.

## Setup

1. Get a free Groq API key at https://console.groq.com (no credit card needed).
2. `cp .env.example .env` and paste your key in.
3. `pip install -r requirements.txt`
4. `streamlit run app.py`
5. Upload `sample_data.csv` to try it immediately, then try your own CSV.

## Example questions to try

- "What columns are in this data and are there any missing values?"
- "What's the total revenue by category?" (quantity x unit_price)
- "Show me a bar chart of average order value by region."
- "Which category has the most orders, and how does that compare to the others?"

## Dataset

> **Before you publish this to your portfolio:** name the real dataset you
> used, where it came from (a link), and any cleaning/preprocessing you did.
> `sample_data.csv` in this repo is a small **synthetic** file generated
> locally purely for testing the app end to end -- swap in a real,
> clearly-sourced public dataset (e.g. Kaggle, UCI, data.gov.in) for the
> version you show recruiters, and say so explicitly in this README.

## Known limitations

- `run_python` executes model-generated code with Python's `exec()`. That's
  an accepted trade-off for a local demo, but a real risk if this is ever
  deployed publicly with untrusted users -- a production version would run
  that tool in a sandboxed subprocess with a timeout, not in-process.
- Chat memory lives only in Streamlit session state; it resets on refresh.
- Groq's free tier is rate-limited (fine for demos, not for heavy concurrent use).

## Possible extensions

- Point `run_sql` at a real database via LangChain's `SQLDatabase` instead of
  a single CSV.
- Cache repeated tool calls.
- Add a fully local/offline mode via Ollama, as a fallback if Groq is down.
- Deploy on Streamlit Community Cloud and link the live app from your portfolio.

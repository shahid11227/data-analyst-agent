"""
Tools the agent can call. Each tool operates on a single in-memory dataset
that the Streamlit app loads via `load_dataset()`.

SECURITY NOTE: `run_python` executes model-generated code with Python's
exec(). That's an accepted trade-off for a local demo / portfolio project,
but it is a real risk if this is ever deployed publicly. A production
version should run that tool in a sandboxed subprocess with a timeout and
resource limits (or use a hosted code-interpreter service) instead of
exec()-ing directly in the app process.
"""

import contextlib
import io

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from langchain_core.tools import tool

# Shared in-memory state: the active dataframe and the most recent chart
# drawn by run_python. The Streamlit app reads `last_chart` after each
# agent turn so it can render it alongside the text reply.
STATE = {"df": None, "last_chart": None}

# One DuckDB connection for the app's lifetime; the active dataframe is
# (re-)registered on it as a table named "df" every time a new CSV loads.
_con = duckdb.connect(database=":memory:")


def load_dataset(df: pd.DataFrame) -> None:
    """Called by the Streamlit app whenever a new CSV is uploaded."""
    STATE["df"] = df
    STATE["last_chart"] = None
    try:
        _con.unregister("df")
    except Exception:
        pass
    _con.register("df", df)


@tool
def eda_summary() -> str:
    """Get a structured exploratory summary of the loaded dataset: shape,
    column types, missing values per column, and descriptive statistics.
    Call this first for any "explore", "summarize", or "profile" request,
    or when you need to know what columns exist before writing SQL/Python.
    """
    df = STATE["df"]
    if df is None:
        return "No dataset is loaded yet."
    parts = [
        f"Shape: {df.shape[0]} rows x {df.shape[1]} columns",
        "\nColumn types:\n" + df.dtypes.to_string(),
        "\nMissing values per column:\n" + df.isna().sum().to_string(),
        "\nSummary statistics:\n" + df.describe(include="all").to_string(),
    ]
    return "\n".join(parts)


@tool
def run_sql(query: str) -> str:
    """Run a read-only SQL query (DuckDB dialect) against the dataset,
    which is registered as a table named `df`. Best for aggregations,
    filters, GROUP BY, sorting, and counts.
    Example: SELECT category, AVG(price) AS avg_price FROM df GROUP BY category ORDER BY avg_price DESC
    """
    if STATE["df"] is None:
        return "No dataset is loaded yet."
    try:
        result = _con.execute(query).df()
    except Exception as exc:
        return f"SQL error: {exc}"
    if result.empty:
        return "Query returned no rows."
    return result.head(50).to_markdown(index=False)


@tool
def run_python(code: str) -> str:
    """Run Python code against the dataset, available as the variable `df`
    (pandas), with `pd` and `plt` also available. Use this for anything SQL
    can't do: custom calculations, multi-step transforms, or charts.
    To show a chart, just create a matplotlib figure -- it is captured
    automatically and shown to the user. print() anything you want
    reported back; the code's return value is not captured automatically.
    """
    df = STATE["df"]
    if df is None:
        return "No dataset is loaded yet."
    plt.close("all")
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(code, {"df": df, "pd": pd, "plt": plt}, {})
    except Exception as exc:
        return f"Error running code: {exc}"
    if plt.get_fignums():
        STATE["last_chart"] = plt.gcf()
    output = buf.getvalue().strip()
    return output if output else "Code ran with no printed output."

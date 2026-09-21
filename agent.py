"""
Builds the LangChain agent: an open-source model served for free by Groq,
wired up with the three data tools in tools.py.
"""

import os

from langchain.agents import create_agent
from langchain_groq import ChatGroq

from tools import eda_summary, run_python, run_sql

SYSTEM_PROMPT = """You are a data analyst agent working with one loaded dataset.

Tool choice:
- Call `eda_summary` first for any explore / summarize / profile / "what's in this data" request.
- Prefer `run_sql` for aggregations, filtering, grouping, sorting, counts -- anything a SQL query naturally expresses.
- Use `run_python` for custom calculations, multi-step logic, or any chart/plot.
- Never invent numbers. Always call a tool to get real values from the data before answering.
- After a tool call, explain the result in plain English -- don't just paste raw tool output back verbatim.
"""


def build_agent():
    if not os.environ.get("GROQ_API_KEY"):
        raise RuntimeError(
            "GROQ_API_KEY is not set. Get a free key at https://console.groq.com "
            "(no credit card needed) and put it in a .env file -- see .env.example."
        )
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
    return create_agent(
        model=llm,
        tools=[eda_summary, run_sql, run_python],
        system_prompt=SYSTEM_PROMPT,
    )
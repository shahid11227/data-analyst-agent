"""
Streamlit front end for the data analyst agent.
Run with: streamlit run app.py
"""

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from agent import build_agent
from tools import STATE, load_dataset

load_dotenv()

st.set_page_config(page_title="Shahid's Data Analyst Agent", page_icon="\U0001F4CA", layout="wide")
st.title("\U0001F4CA Shahid's Data Analyst Agent")
st.caption(
    "Upload a CSV, then ask questions in plain English -- it can profile the "
    "data, write SQL, run custom Python, and draw charts."
)
st.caption(
    "Built by Shahid Ahmad Sheer Gojree · "
    "[Portfolio](https://shahid11227.github.io/shahid_portfolio) · "
    "[LinkedIn](https://www.linkedin.com/in/shahid-gojree-082857389/)"
)

if "agent" not in st.session_state:
    try:
        st.session_state.agent = build_agent()
        st.session_state.agent_error = None
    except Exception as exc:
        st.session_state.agent = None
        st.session_state.agent_error = str(exc)

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.session_state.get("agent_error"):
    st.error(st.session_state.agent_error)

uploaded = st.file_uploader("Upload a CSV", type=["csv"])
if uploaded is not None and st.session_state.get("loaded_file") != uploaded.name:
    df = pd.read_csv(uploaded)
    load_dataset(df)
    st.session_state.loaded_file = uploaded.name
    st.session_state.messages = []
    st.success(f"Loaded **{uploaded.name}** -- {df.shape[0]} rows x {df.shape[1]} columns")
    st.dataframe(df.head())

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("chart") is not None:
            st.pyplot(msg["chart"])

prompt = st.chat_input("Ask about your data...")
if prompt:
    if STATE["df"] is None:
        st.warning("Upload a CSV first.")
    elif st.session_state.agent is None:
        st.warning("The agent isn't configured -- see the error above.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
                result = st.session_state.agent.invoke({"messages": history})
                # If your installed langchain version returns a different
                # shape, print(result) here to see the actual structure.
                reply = result["messages"][-1].content
            st.markdown(reply)
            chart = STATE.get("last_chart")
            if chart is not None:
                st.pyplot(chart)
                STATE["last_chart"] = None

        st.session_state.messages.append(
            {"role": "assistant", "content": reply, "chart": chart}
        )
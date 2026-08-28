import os

import streamlit as st
from dotenv import load_dotenv

from graph import graph

load_dotenv()

st.set_page_config(page_title="Chess Club SQL Assistant", page_icon="♟️")

st.title("♟️ Chess Club SQL Assistant")
st.caption("Ask questions about your chess club database in plain English.")

with st.sidebar:
    st.subheader("Settings")
    st.write(f"**LLM provider:** `{os.environ.get('LLM_PROVIDER', 'ollama')}`")
    if st.button("Clear chat history"):
        st.session_state.history = []
        st.rerun()

if "history" not in st.session_state:
    st.session_state.history = []


def render_turn(question, result):
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        st.write(result["answer"])

        if result.get("sql"):
            with st.expander("SQL used"):
                st.code(result["sql"], language="sql")

        if result.get("results"):
            st.dataframe(result["results"])


for turn in st.session_state.history:
    render_turn(turn["question"], turn["result"])

question = st.chat_input("Ask a question about the chess club data...")

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = graph.invoke({"question": question})
            except Exception as exc:
                st.error(f"Something went wrong: {exc}")
                result = None

        if result is not None:
            st.write(result["answer"])

            if result.get("sql"):
                with st.expander("SQL used"):
                    st.code(result["sql"], language="sql")

            if result.get("results"):
                st.dataframe(result["results"])

    if result is not None:
        st.session_state.history.append({
            "question": question,
            "result": result,
        })

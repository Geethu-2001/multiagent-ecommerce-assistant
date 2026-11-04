import uuid
import streamlit as st
from multiagent.config import get_settings
from multiagent.graph import run_question
from multiagent.llm import check_ollama
from multiagent.agents.database import get_engine

st.set_page_config(page_title="Multi-Agent E-commerce Assistant", page_icon="🛍️", layout="wide")
st.title("🛍️ Multi-Agent E-commerce Research Assistant")
st.caption("LangGraph supervisor · Web scraper · PostgreSQL connector · Reusable summarizer · Local Ollama model")

with st.sidebar:
    st.header("Session & configuration")
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if st.button("＋ New conversation", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    style = st.selectbox("Answer style", ["concise", "detailed", "bullet points", "technical"])
    debug = st.toggle("Show workflow trace", value=False)
    st.divider()
    settings = get_settings()
    ok, message = check_ollama()
    st.write("**Ollama**")
    st.success(message) if ok else st.warning(message)
    st.write("**PostgreSQL**")
    try:
        with get_engine().connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        st.success("Database connection is healthy")
    except Exception as exc:
        st.error(f"Database unavailable ({type(exc).__name__}). Start PostgreSQL and check DATABASE_URL.")
    st.caption(f"Model: `{settings.ollama_model}`")
    st.caption("Do not use real personal or payment data in this demo.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for item in st.session_state.messages:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])
        if item.get("details"):
            with st.expander("Sources, results & execution details"):
                if item["details"].get("web_result"):
                    st.write("**Web retrieval**")
                    st.json(item["details"]["web_result"])
                if item["details"].get("db_result"):
                    st.write("**Database retrieval**")
                    st.json(item["details"]["db_result"])
                if item["details"].get("execution_trace"):
                    st.write("**Workflow trace**", " → ".join(item["details"]["execution_trace"]))

question = st.chat_input("Ask about e-commerce data, provide a public URL, or paste text to summarize…")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Running the selected LangGraph workflow…"):
            result = run_question(question, thread_id=st.session_state.thread_id, answer_style=style)
        answer = result.get("final_answer", "No answer was returned.")
        st.markdown(answer)
        details = {key: result.get(key) for key in ("web_result", "db_result", "execution_trace", "errors") if result.get(key) is not None}
        with st.expander("Sources, results & execution details"):
            if result.get("web_result"):
                st.write("**Web retrieval**")
                st.json(result["web_result"])
            if result.get("db_result"):
                st.write("**Database retrieval**")
                st.json(result["db_result"])
            if debug:
                st.write("**Workflow trace**", " → ".join(result.get("execution_trace", [])))
            if result.get("errors"):
                st.warning("Internal diagnostic: " + "; ".join(result["errors"]))
    st.session_state.messages.append({"role": "assistant", "content": answer, "details": details})

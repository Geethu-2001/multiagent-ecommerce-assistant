from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .supervisor import supervisor_node
from .agents.web_agent import web_graph
from .agents.db_agent import db_graph
from .agents.summarizer import summarizer_graph
from .llm import get_llm


def _clarify(state: AgentState) -> dict:
    return {"final_answer": "Could you clarify what you want to know? You can ask about the e-commerce database, provide a public webpage URL, or paste text to summarize.", "clarification": "Please clarify the request.", "execution_trace": state.get("execution_trace", []) + ["clarify"]}

def _web(state: AgentState) -> dict:
    result = web_graph.invoke(state)
    return {"web_result": result.get("web_result"), "execution_trace": result.get("execution_trace", state.get("execution_trace", []))}

def _db(state: AgentState) -> dict:
    result = db_graph.invoke(state)
    return {"db_result": result.get("db_result"), "execution_trace": result.get("execution_trace", state.get("execution_trace", []))}

def _summary(state: AgentState) -> dict:
    result = summarizer_graph.invoke(state)
    return {"final_answer": result.get("final_answer", "No answer was produced."), "summary_result": result.get("summary_result"), "execution_trace": state.get("execution_trace", []) + ["summarizer"]}

def _combine(state: AgentState) -> dict:
    # Both retrieval components are independent; run them concurrently while preserving partial success.
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as pool:
        web_future = pool.submit(web_graph.invoke, state)
        db_future = pool.submit(db_graph.invoke, state)
        web = web_future.result()
        db = db_future.result()
    return {"web_result": web.get("web_result"), "db_result": db.get("db_result"), "execution_trace": state.get("execution_trace", []) + ["web_scraper", "db_connector", "aggregate_results"]}


def _direct_answer(state: AgentState) -> dict:
    question = state.get("question", "")

    prompt = f"""
You are a helpful assistant.

Answer the user's general question clearly and accurately.
Do not claim to have searched the web or queried the database.
If the question requires current information or facts you cannot
reliably establish, explain that limitation.

User question:
{question}
"""

    response = get_llm().invoke(prompt)

    return {
        "final_answer": str(response.content).strip(),
        "execution_trace": (
            state.get("execution_trace", []) + ["direct_answer"]
        ),
    }


def _route(state: AgentState) -> str:
    return state.get("route", "clarify")

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("supervisor", supervisor_node)
    g.add_node("web_scraper", _web)
    g.add_node("db_connector", _db)
    g.add_node("combined_retrieval", _combine)
    g.add_node("summarizer", _summary)
    g.add_node("clarify", _clarify)
    g.add_node("direct_answer", _direct_answer)
    g.add_edge(START, "supervisor")
    g.add_conditional_edges(
    "supervisor",
    _route,
    {
        "web_scraper": "web_scraper",
        "db_connector": "db_connector",
        "web_and_db": "combined_retrieval",
        "summarizer": "summarizer",
        "direct_answer": "direct_answer",
        "clarify": "clarify",
    },
)

    g.add_edge("web_scraper", "summarizer")
    g.add_edge("db_connector", "summarizer")
    g.add_edge("combined_retrieval", "summarizer")
    g.add_edge("summarizer", END)
    g.add_edge("clarify", END)
    g.add_edge("direct_answer", END)
    return g.compile()

app_graph = build_graph()

def run_question(question: str, thread_id: str = "default", answer_style: str = "concise") -> dict:
    initial: AgentState = {"question": question, "thread_id": thread_id, "answer_style": answer_style, "execution_trace": [], "errors": []}
    try:
        return app_graph.invoke(initial, config={"configurable": {"thread_id": thread_id}, "recursion_limit": 12})
    except Exception as exc:
        # Never pretend an LLM response was generated after a model/provider failure.
        return {**initial, "final_answer": f"The workflow could not complete: {type(exc).__name__}. Check Ollama availability and the configured model. Run `ollama list` and verify OLLAMA_BASE_URL.", "errors": [f"{type(exc).__name__}: {str(exc)[:300]}"]}

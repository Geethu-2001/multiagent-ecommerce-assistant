from langgraph.graph import StateGraph, START, END
from .database import query_database
from ..state import AgentState

def _retrieve_db(state: AgentState) -> dict:
    result = query_database(state.get("question", ""))
    return {"db_result": result, "execution_trace": state.get("execution_trace", []) + ["db_connector"]}

def build_db_graph():
    graph = StateGraph(AgentState)
    graph.add_node("retrieve_db", _retrieve_db)
    graph.add_edge(START, "retrieve_db")
    graph.add_edge("retrieve_db", END)
    return graph.compile()
db_graph = build_db_graph()

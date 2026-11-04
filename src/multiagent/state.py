from typing import Any, TypedDict

class AgentState(TypedDict, total=False):
    question: str
    thread_id: str
    answer_style: str
    route: str
    clarification: str
    web_result: dict[str, Any]
    db_result: dict[str, Any]
    summary_result: dict[str, Any]
    final_answer: str
    errors: list[str]
    execution_trace: list[str]
    sources: list[dict[str, str]]

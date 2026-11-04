# from langgraph.graph import StateGraph, START, END
# from .web_scraper import fetch_webpage
# from ..state import AgentState

# def _retrieve(state: AgentState) -> dict:
#     import re
#     urls = re.findall(r"https?://[^\s<>\]\)\"']+", state.get("question", ""))
#     if not urls:
#         return {"web_result": {"ok": False, "error": "Please include the public webpage URL you want me to retrieve."}}
#     results = [fetch_webpage(url.rstrip(".,")) for url in urls[:3]]
#     if len(results) == 1:
#         result = results[0]
#     else:
#         result = {"ok": any(r.get("ok") for r in results), "pages": results, "urls": [r.get("url", "") for r in results]}
#     return {"web_result": result, "execution_trace": state.get("execution_trace", []) + ["web_scraper"]}

# def build_web_graph():
#     graph = StateGraph(AgentState)
#     graph.add_node("retrieve_web", _retrieve)
#     graph.add_edge(START, "retrieve_web")
#     graph.add_edge("retrieve_web", END)
#     return graph.compile()
# web_graph = build_web_graph()



import re

from langgraph.graph import StateGraph, START, END
from tavily import TavilyClient

from ..config import get_settings
from ..state import AgentState
from .web_scraper import fetch_webpage


def _retrieve(state: AgentState) -> dict:
    question = state.get("question", "")
    trace = state.get("execution_trace", [])

    urls = re.findall(r"""https?://[^\s<>"'\])]+""", question)

    # Case 1: The user supplied a URL; scrape the page.
    if urls:
        results = [
            fetch_webpage(url.rstrip(".,"))
            for url in urls[:3]
        ]

        if len(results) == 1:
            result = results[0]
        else:
            result = {
                "ok": any(r.get("ok") for r in results),
                "pages": results,
                "urls": [r.get("url", "") for r in results],
                "content": "\n\n".join(
                    f"Title: {r.get('title', 'Unknown')}\n"
                    f"URL: {r.get('url', '')}\n"
                    f"{r.get('content', r.get('error', 'No content'))}"
                    for r in results
                ),
            }

        return {
            "web_result": result,
            "execution_trace": trace + ["web_scraper"],
        }

    # Case 2: No URL supplied; search the internet.
    settings = get_settings()

    if not settings.tavily_api_key:
        return {
            "web_result": {
                "ok": False,
                "error": (
                    "Web search requires TAVILY_API_KEY. "
                    "Add it to .env and restart the application."
                ),
            },
            "execution_trace": trace + ["web_search"],
        }

    try:
        client = TavilyClient(api_key=settings.tavily_api_key)

        response = client.search(
            query=question,
            search_depth="basic",
            max_results=5,
            include_answer=True,
        )

        results = response.get("results", [])

        content_parts = []

        for index, item in enumerate(results, start=1):
            content_parts.append(
                f"Source {index}: {item.get('title', 'Untitled')}\n"
                f"URL: {item.get('url', '')}\n"
                f"Content: {item.get('content', '')}"
            )

        search_answer = response.get("answer")
        if search_answer:
            content_parts.insert(
                0,
                f"Search engine summary:\n{search_answer}",
            )

        content = "\n\n".join(content_parts)

        return {
            "web_result": {
                "ok": bool(results),
                "query": question,
                "title": "Web search results",
                "answer": search_answer,
                "results": results,
                "headings": [],
                "content": content,
                "links": [
                    {
                        "text": item.get("title", ""),
                        "url": item.get("url", ""),
                    }
                    for item in results
                ],
                "error": None if results else "No search results were found.",
            },
            "execution_trace": trace + ["web_search"],
        }

    except Exception as exc:
        return {
            "web_result": {
                "ok": False,
                "error": f"Web search failed ({type(exc).__name__}).",
            },
            "execution_trace": trace + ["web_search"],
        }


def build_web_graph():
    graph = StateGraph(AgentState)
    graph.add_node("retrieve_web", _retrieve)
    graph.add_edge(START, "retrieve_web")
    graph.add_edge("retrieve_web", END)
    return graph.compile()


web_graph = build_web_graph()

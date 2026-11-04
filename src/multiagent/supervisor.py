
# import re
# from .state import AgentState

# WEB_TERMS = (
#     "website", "webpage", "url", "site", "from this link",
#     "scrape", "fetch", "search the web", "web search",
#     "search online", "search the internet", "latest",
#     "current", "today", "recent", "github", "news",
#     "in 2026", "this year", "who won", "price today",
#     "amazon", "on amazon",
#     "best selling", "best-selling", "most selling",
# )

# DB_TERMS = (
#     "database", "customer", "customers", "order", "orders",
#     "product", "products", "stock", "shipment", "payment",
#     "revenue", "sales", "category", "categories",
#     "user id", "customer id",
# )

# SUMMARY_TERMS = (
#     "summarize", "summarise", "summary",
#     "summarize this", "summarise this",
# )


# # 
# def route_request(question: str) -> str:
#     q = question.lower()
#     has_url = bool(re.search(r"https?://", q))

#     web = has_url or any(term in q for term in WEB_TERMS)
#     db = any(term in q for term in DB_TERMS)

#     # Detect an explicit request to use the local database.
#     explicit_db = any(term in q for term in (
#         "database",
#         "my data",
#         "our data",
#         "local dataset",
#         "my dataset",
#         "e-commerce database",
#     ))

#     comparison = any(term in q for term in (
#         "compare",
#         "comparison",
#         "against",
#         "versus",
#         " vs ",
#     ))

#     # Use both agents only when the user explicitly requests a comparison.
#     if web and db and explicit_db and comparison:
#         return "web_and_db"

#     # Explicit local database requests take priority over generic words
#     # such as "product", "sales", and "best-selling".
#     if explicit_db and db:
#         return "db_connector"

#     # External research should not query the local database by default.
#     if web:
#         return "web_scraper"

#     if any(term in q for term in SUMMARY_TERMS):
#         return "summarizer"

#     if db:
#         return "db_connector"

#     if len(question.strip()) < 20:
#         return "clarify"

#     return "summarizer"


# def supervisor_node(state: AgentState) -> dict:
#     route = route_request(state.get("question", ""))
#     trace = state.get("execution_trace", [])

#     return {
#         "route": route,
#         "execution_trace": trace + [f"supervisor:{route}"],
#     }


from typing import Literal

from pydantic import BaseModel, Field

from .llm import get_llm
from .state import AgentState


class RouteDecision(BaseModel):
    route: Literal[
        "db_connector",
        "web_scraper",
        "web_and_db",
        "summarizer",
        "direct_answer",
        "clarify",
    ]
    reason: str = Field(
        description="Brief explanation for choosing this route"
    )


def supervisor_node(state: AgentState) -> dict:
    question = state.get("question", "").strip()

    if not question:
        return {
            "route": "clarify",
            "execution_trace": (
                state.get("execution_trace", []) + ["supervisor:clarify"]
            ),
        }

    
    prompt = f"""
    You are an intelligent routing supervisor for an e-commerce assistant.

    Choose the route that provides all information needed to answer the
    user's request. Interpret the full meaning of the request.

    Available routes:

    - db_connector:
    Retrieve internal business data from PostgreSQL, including our
    customers, users, orders, products, prices, inventory, payments,
    and sales.

    - web_scraper:
    Search the web or retrieve webpages for external information,
    current facts, news, competitors, public rankings, and trends.

    - web_and_db:
    Use BOTH PostgreSQL and web search when the answer requires
    internal business data AND external information.
    Examples include comparing our prices with competitors,
    comparing our sales with market trends, and evaluating our products
    against external alternatives.

    - summarizer:
    Summarize user-provided text or evidence that has already been
    retrieved. Do not use this route to retrieve missing evidence.

    - direct_answer:
    Answer general questions that do not require current external
    research or private application data.

    - clarify:
    Ask for clarification when the request is genuinely ambiguous
    or cannot be safely interpreted.

    Decision principles:

    1. Determine what information is needed to answer the entire question.
    2. Identify whether that information is internal, external, or both.
    3. Choose web_and_db whenever BOTH sources are necessary.
    4. A comparison between our business and external competitors
    generally requires both sources.
    5. Current public information requires web research.
    6. Questions about our own customers, orders, products, or sales
    require database retrieval.
    7. Do not select a route merely because a word appears in the question.
    8. Return exactly one valid route and a brief explanation.

    User request:
    {question}
    """

    try:
        decision = get_llm().with_structured_output(
            RouteDecision
        ).invoke(prompt)

        route = decision.route

    except Exception:
        # Safe fallback if the model fails or returns invalid output.
        route = "clarify"

    return {
        "route": route,
        "execution_trace": (
            state.get("execution_trace", [])
            + [f"supervisor:{route}"]
        ),
    }

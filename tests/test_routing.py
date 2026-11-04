# from multiagent.supervisor import route_request

# def test_routes_url_to_web():
#     assert route_request("Fetch this page https://example.com/item") == "web_scraper"

# def test_routes_db_questions():
#     assert route_request("Show the five most expensive products in the database") == "db_connector"

# def test_routes_direct_summary():
#     assert route_request("Summarize this: The shop opened in 2020 and sells books.") == "summarizer"

# def test_routes_combined():
#     assert route_request("Compare this product with our database: https://example.com/item") == "web_and_db"

# def test_clarifies_short_ambiguous_request():
#     assert route_request("help") == "clarify"


from unittest.mock import patch

from multiagent.supervisor import RouteDecision, supervisor_node


def test_routes_database_question():
    decision = RouteDecision(
        route="db_connector",
        reason="The question asks about local customer orders.",
    )

    with patch(
        "multiagent.supervisor.get_llm"
    ) as mock_get_llm:
        mock_get_llm.return_value.with_structured_output.return_value.invoke.return_value = decision

        result = supervisor_node({
            "question": "Who are our five most recent customers?",
            "execution_trace": [],
        })

    assert result["route"] == "db_connector"
    assert result["execution_trace"] == ["supervisor:db_connector"]


def test_routes_current_information_to_web():
    decision = RouteDecision(
        route="web_scraper",
        reason="The question requires current external information.",
    )

    with patch(
        "multiagent.supervisor.get_llm"
    ) as mock_get_llm:
        mock_get_llm.return_value.with_structured_output.return_value.invoke.return_value = decision

        result = supervisor_node({
            "question": "Who is the highest-paid actor in 2026?",
            "execution_trace": [],
        })

    assert result["route"] == "web_scraper"


def test_routes_comparison_to_both_sources():
    decision = RouteDecision(
        route="web_and_db",
        reason="The question requires internal and external evidence.",
    )

    with patch(
        "multiagent.supervisor.get_llm"
    ) as mock_get_llm:
        mock_get_llm.return_value.with_structured_output.return_value.invoke.return_value = decision

        result = supervisor_node({
            "question": "Compare our prices with competitors.",
            "execution_trace": [],
        })

    assert result["route"] == "web_and_db"


def test_empty_question_uses_clarify():
    result = supervisor_node({
        "question": "",
        "execution_trace": [],
    })

    assert result["route"] == "clarify"


def test_llm_failure_uses_safe_fallback():
    with patch(
        "multiagent.supervisor.get_llm",
        side_effect=RuntimeError("Model unavailable"),
    ):
        result = supervisor_node({
            "question": "What is an API?",
            "execution_trace": [],
        })

    assert result["route"] == "clarify"

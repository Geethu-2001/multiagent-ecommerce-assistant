from multiagent.agents.summarizer import build_summarizer_graph

def test_empty_input_does_not_call_model():
    graph = build_summarizer_graph()
    result = graph.invoke({"question": "", "execution_trace": []})
    assert "no retrieved content" in result["final_answer"].lower()

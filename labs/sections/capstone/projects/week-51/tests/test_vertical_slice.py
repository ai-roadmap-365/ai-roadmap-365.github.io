import pytest
from examples.vertical_slice import CapstoneVerticalSlice, AnswerPayload

def test_vertical_slice_retrieval():
    app = CapstoneVerticalSlice()
    docs = app.hybrid_retrieval("SLA uptime")
    assert len(docs) == 2
    assert docs[0]["id"] == "doc1"

def test_vertical_slice_tool_execution():
    app = CapstoneVerticalSlice()
    result = app.execute_tool("calc_penalty", base=2000, rate=0.10)
    assert result == 200.0

def test_vertical_slice_end_to_end_query():
    app = CapstoneVerticalSlice()
    res = app.run_query("What is SLA?")
    assert res["status"] == "SUCCESS"
    assert res["retrieved_doc_count"] == 2
    assert res["answer"]["confidence_score"] == 0.96
    assert "doc1" in res["answer"]["citations"]
    assert res["tool_result"] == 50.0

def test_vertical_slice_latency_budget():
    app = CapstoneVerticalSlice()
    res = app.run_query("Check latency")
    assert res["latency_ms"] < 1500.0

def test_pydantic_schema_integrity():
    app = CapstoneVerticalSlice()
    res = app.run_query("Test schema")
    payload = AnswerPayload(**res["answer"])
    assert payload.confidence_score >= 0.0
    assert len(payload.detailed_points) > 0

def test_invalid_tool_handling():
    app = CapstoneVerticalSlice()
    with pytest.raises(ValueError):
        app.execute_tool("nonexistent_tool")

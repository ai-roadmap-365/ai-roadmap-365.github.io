import pytest
import time
from examples.tracing_engine import TraceTelemetryEngine, Span

def test_start_root_trace():
    engine = TraceTelemetryEngine()
    root = engine.start_trace("Query_Root")
    assert root.kind == "ROOT"
    assert root.parent_id is None
    assert root.span_id in engine.traces

def test_create_child_span_and_hierarchy():
    engine = TraceTelemetryEngine()
    root = engine.start_trace("Root")
    child = engine.create_child_span(root, "LLM_Call", "LLM")
    assert child.parent_id == root.span_id
    assert len(root.children) == 1
    assert root.children[0].name == "LLM_Call"

def test_span_timing_and_attributes():
    span = Span(name="TestSpan", kind="TOOL")
    span.set_attribute("tool.name", "weather_api")
    time.sleep(0.01)
    span.finish()
    assert span.duration_ms >= 5.0
    assert span.attributes["tool.name"] == "weather_api"

def test_calculate_cost():
    cost = TraceTelemetryEngine.calculate_cost(prompt_tokens=1000, completion_tokens=500)
    # (1000 * 3 / 1M) + (500 * 15 / 1M) = 0.003 + 0.0075 = 0.0105
    assert cost == 0.0105

def test_trace_to_dict_serialization():
    engine = TraceTelemetryEngine()
    root = engine.start_trace("Main_Pipeline")
    child = engine.create_child_span(root, "Vector_Search", "RETRIEVER")
    child.finish()
    root.finish()
    
    data = root.to_dict()
    assert data["name"] == "Main_Pipeline"
    assert len(data["children"]) == 1
    assert data["children"][0]["name"] == "Vector_Search"

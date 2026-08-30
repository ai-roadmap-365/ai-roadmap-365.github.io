import pytest
from examples.react_engine import ReActEngine

def calc_fn(expr: str) -> str:
    return str(eval(expr, {"__builtins__": None}, {}))

def search_fn(query: str) -> str:
    if "seattle" in query.lower():
        return "Seattle population is 750000"
    return "No match found."

@pytest.fixture
def engine():
    eng = ReActEngine()
    eng.register_tool("calculate", calc_fn)
    eng.register_tool("search_kb", search_fn)
    return eng

def test_parse_final_answer(engine):
    resp = "Thought: I know the answer directly.\nFinal Answer: Paris is the capital of France."
    res = engine.execute_step(resp)
    assert res["status"] == "COMPLETE"
    assert res["final_answer"] == "Paris is the capital of France."
    assert "Paris" in res["thought"] or "directly" in res["thought"]

def test_parse_and_execute_valid_action(engine):
    resp = 'Thought: Search for Seattle population.\nAction: search_kb({"query": "Seattle"})'
    res = engine.execute_step(resp)
    assert res["status"] == "CONTINUE"
    assert res["tool"] == "search_kb"
    assert "750000" in res["observation"]

def test_syntax_error_handling(engine):
    # Malformed JSON with unquoted key and trailing comma
    resp = 'Thought: Run calculation.\nAction: calculate({expr: 100 + 50,})'
    res = engine.execute_step(resp)
    assert res["status"] == "CONTINUE"
    assert "JSON parse error" in res["observation"]

def test_unknown_tool_handling(engine):
    resp = 'Thought: Use missing tool.\nAction: nonexistent_tool({"data": 123})'
    res = engine.execute_step(resp)
    assert res["status"] == "CONTINUE"
    assert "does not exist in registry" in res["observation"]

def test_full_trajectory_accumulation(engine):
    s1 = 'Thought: Need Seattle pop.\nAction: search_kb({"query": "Seattle"})'
    engine.execute_step(s1)
    s2 = 'Thought: Need 20% growth.\nAction: calculate({"expr": "750000 * 1.20"})'
    engine.execute_step(s2)
    s3 = 'Thought: Done.\nFinal Answer: Projected population is 900,000.'
    res3 = engine.execute_step(s3)
    assert res3["status"] == "COMPLETE"
    assert len(engine.scratchpad) == 3
    assert "900000" in engine.scratchpad[1]

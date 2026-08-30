import pytest
from examples.scratch_agent import PurePythonAgent

@pytest.fixture
def agent():
    return PurePythonAgent(max_steps=6, window_size=4)

def test_single_turn_final_answer(agent):
    resp = "Thought: I know the answer directly.\nFinal Answer: 42 is the answer."
    res = agent.step(resp)
    assert res["status"] == "COMPLETE"
    assert res["final_answer"] == "42 is the answer."
    assert len(agent.trajectory) == 2

def test_tool_calculator_execution(agent):
    resp = 'Thought: Calculate 25 * 4.\nAction: calculator({"expr": "25 * 4"})'
    res = agent.step(resp)
    assert res["status"] == "CONTINUE"
    assert res["observation"] == "100"
    assert len(agent.trajectory) == 3

def test_memory_storage_and_retrieval(agent):
    s1 = 'Thought: Store value.\nAction: set_memory({"key": "status", "value": "active"})'
    agent.step(s1)
    assert agent.memory_store.get("status") == "active"
    
    s2 = 'Thought: Retrieve value.\nAction: get_memory({"key": "status"})'
    res2 = agent.step(s2)
    assert "active" in res2["observation"]

def test_sliding_window_prompt_compaction(agent):
    # Add 6 steps to trigger window size 4 compaction
    for i in range(3):
        agent.step(f'Thought: Step {i}\nAction: calculator({{"expr": "{i} + 1"}})')
        
    prompt = agent.render_prompt("Test Goal")
    assert "SYSTEM: You are an autonomous AI agent." in prompt
    assert "GOAL: Test Goal" in prompt
    assert "[System Notice:" in prompt
    assert "earlier steps compacted" in prompt

def test_search_kb_and_safe_math(agent):
    resp = 'Thought: Query Mars project.\nAction: search_kb({"query": "project mars"})'
    res = agent.step(resp)
    assert "$450 million" in res["observation"]

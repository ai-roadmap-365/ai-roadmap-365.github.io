import pytest
from examples.agent_state_machine import AgentState, AgentTrajectory, ToolRegistry, AgentRuntime

def safe_calc(expr: str) -> str:
    return str(eval(expr, {"__builtins__": None}, {}))

def mock_search(query: str) -> str:
    if "python" in query.lower():
        return "Python 3.14 includes performance enhancements."
    return "No records found."

@pytest.fixture
def registry():
    reg = ToolRegistry()
    reg.register("calculator", safe_calc)
    reg.register("search", mock_search)
    return reg

def test_tool_registry_execution(registry):
    assert registry.execute("calculator", "12 * 12") == "144"
    assert "Python 3.14" in registry.execute("search", "python release")
    assert "Error: Tool 'unknown' not found" in registry.execute("unknown", "")

def test_agent_single_pass_final_answer(registry):
    runtime = AgentRuntime(registry, max_steps=5)
    res = runtime.step_loop("Tell me a joke")
    assert res["final_state"] == AgentState.FINAL_ANSWER.value
    assert res["step_count"] == 1
    assert "THINKING" in res["transitions"]
    assert "FINAL_ANSWER" in res["transitions"]

def test_agent_multi_step_tool_execution(registry):
    runtime = AgentRuntime(registry, max_steps=5)
    mock_decisions = [
        {"type": "tool_call", "thought": "Calculate 40 + 2", "tool": "calculator", "args": "40 + 2"},
        {"type": "final_answer", "content": "The answer is 42"}
    ]
    res = runtime.step_loop("What is 40 + 2?", mock_decisions=mock_decisions)
    assert res["final_state"] == AgentState.FINAL_ANSWER.value
    assert res["step_count"] == 2
    assert "TOOL_CALL" in res["transitions"]
    assert "OBSERVING" in res["transitions"]
    assert "[OBSERVATION]: 42" in res["scratchpad"]

def test_agent_max_steps_exceeded(registry):
    runtime = AgentRuntime(registry, max_steps=2)
    mock_decisions = [
        {"type": "tool_call", "thought": "Step 1", "tool": "calculator", "args": "1+1"},
        {"type": "tool_call", "thought": "Step 2", "tool": "calculator", "args": "2+2"},
        {"type": "tool_call", "thought": "Step 3", "tool": "calculator", "args": "3+3"}
    ]
    res = runtime.step_loop("Infinite task", mock_decisions=mock_decisions)
    assert res["final_state"] == AgentState.MAX_STEPS_EXCEEDED.value

def test_agent_cycle_detection(registry):
    runtime = AgentRuntime(registry, max_steps=5)
    mock_decisions = [
        {"type": "tool_call", "thought": "Try calc", "tool": "calculator", "args": "100 / 0"},
        {"type": "tool_call", "thought": "Try same calc again", "tool": "calculator", "args": "100 / 0"}
    ]
    res = runtime.step_loop("Failing calculation", mock_decisions=mock_decisions)
    assert res["final_state"] == AgentState.CYCLE_DETECTED.value

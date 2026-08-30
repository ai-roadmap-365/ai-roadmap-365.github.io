import pytest
from examples.agent import AgentOrchestrator

def test_tool_registration():
    agent = AgentOrchestrator(model_fn=lambda p: "")
    agent.register_tool("calc", "Calculator", {"a": "int", "b": "int"}, lambda a, b: a + b)
    assert "calc" in agent.tool_registry
    res = agent._execute_sandboxed_tool("calc", {"a": 5, "b": 10})
    assert res == "15"

def test_tool_not_found_handling():
    agent = AgentOrchestrator(model_fn=lambda p: "")
    res = agent._execute_sandboxed_tool("missing_tool", {})
    assert "ERROR: Tool 'missing_tool' not found" in res

def test_successful_multi_turn_agent_execution():
    step = 0
    def mock_llm(p: str) -> str:
        nonlocal step
        step += 1
        if step == 1:
            return '{"thought": "Fetch data", "action": "fetch", "action_input": {"key": "revenue"}}'
        return '{"thought": "Synthesize", "action": "FINAL_ANSWER", "action_input": {"answer": "Revenue is $10M"}}'

    agent = AgentOrchestrator(model_fn=mock_llm)
    agent.register_tool("fetch", "Fetch metric", {}, lambda key: 10000000)
    
    result = agent.run_agent("What is revenue?")
    assert result["status"] == "SUCCESS"
    assert result["total_turns"] == 2
    assert "Revenue is $10M" in result["final_answer"]
    assert len(result["checkpoints"]) == 2

def test_max_turns_exceeded_safety_guard():
    # Model that keeps calling tools forever
    def infinite_loop_llm(p: str) -> str:
        return '{"thought": "Keep going", "action": "noop", "action_input": {}}'

    agent = AgentOrchestrator(model_fn=infinite_loop_llm, max_turns=3)
    agent.register_tool("noop", "No operation", {}, lambda: "ok")
    
    result = agent.run_agent("Do endless work")
    assert result["status"] == "MAX_TURNS_EXCEEDED"
    assert result["total_turns"] == 3
    assert len(result["checkpoints"]) == 3

def test_tool_exception_recovery():
    def failing_tool(): raise ValueError("Database timeout")
    agent = AgentOrchestrator(model_fn=lambda p: "")
    agent.register_tool("fail", "Failing tool", {}, failing_tool)
    res = agent._execute_sandboxed_tool("fail", {})
    assert "ERROR executing tool 'fail'" in res

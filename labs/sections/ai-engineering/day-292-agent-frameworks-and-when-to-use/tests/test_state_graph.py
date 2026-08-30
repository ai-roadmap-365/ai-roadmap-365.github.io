import pytest
from examples.state_graph import StateGraphEngine

def node_planner(state):
    retries = state.get("retries", 0)
    if retries == 0:
        return {"plan": "INVALID_SQL", "retries": 1}
    return {"plan": "SELECT * FROM users;", "retries": retries + 1}

def node_validator(state):
    plan = state.get("plan", "")
    is_valid = plan.startswith("SELECT")
    return {"is_valid": is_valid}

def router_validator(state):
    return "VALID" if state.get("is_valid") else "INVALID"

def node_approval(state):
    return {"requires_human_approval": True}

def node_executor(state):
    return {"status": "EXECUTED_SUCCESSFULLY", "result": [1, 2, 3]}

@pytest.fixture
def workflow():
    g = StateGraphEngine()
    g.add_node("planner", node_planner)
    g.add_node("validator", node_validator)
    g.add_node("approval", node_approval)
    g.add_node("executor", node_executor)
    
    g.set_entry_point("planner")
    g.add_edge("planner", "validator")
    g.add_conditional_edges(
        "validator",
        router_validator,
        {"VALID": "approval", "INVALID": "planner"}
    )
    g.add_edge("approval", "executor")
    g.add_edge("executor", "END")
    return g

def test_cyclic_retry_and_pause(workflow):
    res = workflow.run({"goal": "Query users", "is_approved": False})
    # Should loop once on invalid SQL, then pause at approval gate
    assert res["status"] == "PAUSED_FOR_HUMAN_APPROVAL"
    assert res["is_valid"] is True
    assert res["retries"] == 2
    assert len(workflow.checkpoints) >= 3

def test_resume_after_approval(workflow):
    # First run pauses
    res = workflow.run({"goal": "Query users", "is_approved": False})
    assert res["status"] == "PAUSED_FOR_HUMAN_APPROVAL"
    
    # Resume with approval
    res["is_approved"] = True
    workflow.set_entry_point("executor")
    res_final = workflow.run(res)
    assert res_final["status"] == "EXECUTED_SUCCESSFULLY"
    assert res_final["result"] == [1, 2, 3]

def test_linear_graph_execution():
    g = StateGraphEngine()
    g.add_node("step1", lambda s: {"count": s.get("count", 0) + 1})
    g.add_node("step2", lambda s: {"count": s.get("count", 0) * 10})
    g.set_entry_point("step1")
    g.add_edge("step1", "step2")
    g.add_edge("step2", "END")
    
    res = g.run({"count": 5})
    assert res["count"] == 60
    assert len(g.checkpoints) == 2

def test_max_steps_guard():
    g = StateGraphEngine()
    g.add_node("infinite_loop", lambda s: s)
    g.set_entry_point("infinite_loop")
    g.add_edge("infinite_loop", "infinite_loop")
    
    res = g.run({}, max_steps=4)
    assert "Max graph execution steps exceeded" in res["error"]

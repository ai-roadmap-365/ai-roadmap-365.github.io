import pytest
from examples.multi_agent_system import AgentMessage, MessageBus, MultiAgentSupervisorSystem

def test_message_bus_filtering():
    bus = MessageBus()
    bus.send(AgentMessage("agent_a", "agent_b", "Hello B", "CHAT"))
    bus.send(AgentMessage("agent_a", "agent_c", "Hello C", "CHAT"))
    bus.send(AgentMessage("agent_a", "BROADCAST", "Hello All", "ANNOUNCE"))
    
    b_msgs = bus.get_messages_for("agent_b")
    assert len(b_msgs) == 2
    assert b_msgs[0].content == "Hello B"
    assert b_msgs[1].content == "Hello All"

def test_multi_agent_workflow_success():
    system = MultiAgentSupervisorSystem(max_rounds=5)
    res = system.run("Analyze Q3 revenue report")
    assert res["status"] == "SUCCESS"
    assert res["rounds"] == 3
    assert "$12.4 Billion" in res["final_answer"]
    assert res["message_count"] >= 4

def test_researcher_fact_extraction():
    system = MultiAgentSupervisorSystem()
    ans = system._researcher_turn("Get revenue stats")
    assert "12.4 Billion" in ans

def test_critic_evaluation_logic():
    system = MultiAgentSupervisorSystem()
    assert "PASS" in system._critic_turn("Draft with 12.4 Billion revenue")
    assert "REVISE" in system._critic_turn("Draft with missing info")

def test_max_rounds_safety():
    system = MultiAgentSupervisorSystem(max_rounds=1)
    res = system.run("Analyze revenue")
    # Round 1 only delegates, so max_rounds=1 will terminate with MAX_ROUNDS_EXCEEDED
    assert res["status"] == "MAX_ROUNDS_EXCEEDED"

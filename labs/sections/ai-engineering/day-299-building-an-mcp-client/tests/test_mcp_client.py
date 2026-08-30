import pytest
from examples.mcp_client import MockMCPServerInstance, AutonomousMCPAgent

def test_multi_server_registration():
    agent = AutonomousMCPAgent()
    srv1 = MockMCPServerInstance("db", {"sql_query": lambda args: "10 rows"})
    srv2 = MockMCPServerInstance("fs", {"read_log": lambda args: "log entries"})
    agent.register_server("db", srv1)
    agent.register_server("fs", srv2)
    
    assert len(agent.unified_tools) == 2
    tool_names = [t["name"] for t in agent.unified_tools]
    assert "sql_query" in tool_names
    assert "read_log" in tool_names

def test_tool_routing_execution():
    agent = AutonomousMCPAgent()
    srv1 = MockMCPServerInstance("db", {"sql_query": lambda args: "Result A"})
    srv2 = MockMCPServerInstance("fs", {"read_log": lambda args: "Result B"})
    agent.register_server("db", srv1)
    agent.register_server("fs", srv2)
    
    res1 = agent.execute_tool("sql_query", {})
    assert res1 == "Result A"
    
    res2 = agent.execute_tool("read_log", {})
    assert res2 == "Result B"

def test_unknown_tool_routing():
    agent = AutonomousMCPAgent()
    res = agent.execute_tool("unknown_action", {})
    assert "not found" in res.lower()

def test_initialization_handshake():
    srv = MockMCPServerInstance("test", {})
    res_str = srv.handle_line('{"jsonrpc": "2.0", "id": 1, "method": "initialize"}')
    assert "2024-11-05" in res_str

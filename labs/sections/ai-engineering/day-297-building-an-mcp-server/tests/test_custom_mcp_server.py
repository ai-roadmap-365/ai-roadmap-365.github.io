import pytest
from examples.custom_mcp_server import CustomMCPServer

def test_tool_registration_and_schema():
    server = CustomMCPServer("test-server")
    
    @server.tool()
    def add_numbers(a: int, b: int = 10) -> int:
        """Add two numbers together."""
        return a + b
        
    tools = server.list_tools()
    assert len(tools) == 1
    t = tools[0]
    assert t["name"] == "add_numbers"
    assert t["description"] == "Add two numbers together."
    assert t["inputSchema"]["properties"]["a"]["type"] == "integer"
    assert t["inputSchema"]["properties"]["b"]["type"] == "integer"
    assert t["inputSchema"]["required"] == ["a"]

def test_tool_call_success():
    server = CustomMCPServer("calc")
    
    @server.tool()
    def multiply(x: float, y: float) -> float:
        return x * y
        
    res = server.call_tool("multiply", {"x": 3.5, "y": 2.0})
    assert res["isError"] is False
    assert res["content"][0]["text"] == "7.0"

def test_tool_call_missing_arg_error():
    server = CustomMCPServer("calc")
    
    @server.tool()
    def divide(a: float, b: float) -> float:
        return a / b
        
    res = server.call_tool("divide", {"a": 10.0}) # missing b
    assert res["isError"] is True
    assert "missing" in res["content"][0]["text"].lower()

def test_tool_call_runtime_exception():
    server = CustomMCPServer("calc")
    
    @server.tool()
    def divide(a: float, b: float) -> float:
        return a / b
        
    res = server.call_tool("divide", {"a": 10.0, "b": 0.0})
    assert res["isError"] is True
    assert "division by zero" in res["content"][0]["text"]

def test_unknown_tool_call():
    server = CustomMCPServer("calc")
    res = server.call_tool("nonexistent", {})
    assert res["isError"] is True
    assert "not found" in res["content"][0]["text"]

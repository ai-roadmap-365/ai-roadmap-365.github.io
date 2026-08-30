import pytest
import json
from examples.mcp_protocol import MCPProtocolHandler

def test_mcp_initialize():
    server = MCPProtocolHandler("test-server", "2.0.0")
    res_str = server.handle_message('{"jsonrpc": "2.0", "id": 1, "method": "initialize"}')
    assert res_str is not None
    res = json.loads(res_str)
    assert res["result"]["protocolVersion"] == "2024-11-05"
    assert res["result"]["serverInfo"]["name"] == "test-server"

def test_mcp_notification_ignored():
    server = MCPProtocolHandler()
    res_str = server.handle_message('{"jsonrpc": "2.0", "method": "notifications/initialized"}')
    assert res_str is None

def test_mcp_tools_list_and_call():
    server = MCPProtocolHandler()
    server.register_tool(
        "add",
        "Add numbers",
        {"type": "object"},
        lambda args: args["a"] + args["b"]
    )
    # List
    list_str = server.handle_message('{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}')
    list_res = json.loads(list_str)
    assert len(list_res["result"]["tools"]) == 1
    assert list_res["result"]["tools"][0]["name"] == "add"
    
    # Call
    call_str = server.handle_message('{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "add", "arguments": {"a": 10, "b": 32}}}')
    call_res = json.loads(call_str)
    assert call_res["result"]["content"][0]["text"] == "42"
    assert call_res["result"]["isError"] is False

def test_mcp_unknown_tool():
    server = MCPProtocolHandler()
    call_str = server.handle_message('{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "nonexistent"}}')
    call_res = json.loads(call_str)
    assert "error" in call_res
    assert call_res["error"]["code"] == -32601

def test_mcp_parse_error():
    server = MCPProtocolHandler()
    res_str = server.handle_message('INVALID JSON {')
    res = json.loads(res_str)
    assert res["error"]["code"] == -32700

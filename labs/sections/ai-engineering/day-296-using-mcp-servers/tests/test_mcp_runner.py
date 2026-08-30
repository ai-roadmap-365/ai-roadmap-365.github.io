import pytest
import json
from examples.mcp_runner import MCPConfigParser, LocalMCPRunner

def test_config_parser_valid():
    raw = '{"mcpServers": {"sqlite": {"command": "python", "args": ["-u", "server.py"]}}}'
    servers = MCPConfigParser.parse_config(raw)
    assert "sqlite" in servers
    assert servers["sqlite"]["command"] == "python"

def test_config_parser_invalid():
    with pytest.raises(ValueError):
        MCPConfigParser.parse_config('{"wrongKey": {}}')

def test_mcp_runner_initialize():
    runner = LocalMCPRunner("demo-sqlite", {"command": "python"})
    res = runner.initialize()
    assert res["result"]["protocolVersion"] == "2024-11-05"
    assert res["result"]["serverInfo"]["name"] == "demo-sqlite"

def test_mcp_runner_list_tools():
    runner = LocalMCPRunner("demo-sqlite", {"command": "python"})
    tools = runner.list_tools()
    assert len(tools) == 1
    assert tools[0]["name"] == "get_status"

def test_mcp_runner_call_tool():
    runner = LocalMCPRunner("demo-sqlite", {"command": "python"})
    res = runner.call_tool("get_status", {})
    assert res["isError"] is False
    content_data = json.loads(res["content"][0]["text"])
    assert content_data["status"] == "ONLINE"

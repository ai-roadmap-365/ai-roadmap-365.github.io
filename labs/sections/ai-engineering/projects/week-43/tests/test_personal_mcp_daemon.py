import pytest
import json
from examples.personal_mcp_daemon import PersonalMCPDaemon

def test_daemon_initialize_and_tools():
    daemon = PersonalMCPDaemon(":memory:")
    
    init_res = json.loads(daemon.handle_request('{"jsonrpc": "2.0", "id": 1, "method": "initialize"}'))
    assert init_res["result"]["serverInfo"]["name"] == "personal-mcp-daemon"
    
    tools_res = json.loads(daemon.handle_request('{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}'))
    tools = [t["name"] for t in tools_res["result"]["tools"]]
    assert "save_memo" in tools
    assert "search_memos" in tools
    assert "add_todo" in tools

def test_daemon_tool_calls():
    daemon = PersonalMCPDaemon(":memory:")
    
    save_req = json.dumps({
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "save_memo", "arguments": {"title": "Roadmap", "content": "Complete Week 43"}}
    })
    save_res = json.loads(daemon.handle_request(save_req))
    assert "Saved memo ID: 1" in save_res["result"]["content"][0]["text"]
    
    search_req = json.dumps({
        "jsonrpc": "2.0", "id": 4, "method": "tools/call",
        "params": {"name": "search_memos", "arguments": {"keyword": "Week 43"}}
    })
    search_res = json.loads(daemon.handle_request(search_req))
    assert "Roadmap" in search_res["result"]["content"][0]["text"]

def test_daemon_resources():
    daemon = PersonalMCPDaemon(":memory:")
    
    add_req = json.dumps({
        "jsonrpc": "2.0", "id": 5, "method": "tools/call",
        "params": {"name": "add_todo", "arguments": {"task": "Write project tests"}}
    })
    daemon.handle_request(add_req)
    
    read_req = json.dumps({
        "jsonrpc": "2.0", "id": 6, "method": "resources/read",
        "params": {"uri": "memo://pending-todos"}
    })
    read_res = json.loads(daemon.handle_request(read_req))
    assert "Write project tests" in read_res["result"]["contents"][0]["text"]

def test_daemon_prompts():
    daemon = PersonalMCPDaemon(":memory:")
    prompt_req = json.dumps({
        "jsonrpc": "2.0", "id": 7, "method": "prompts/get",
        "params": {"name": "standup", "arguments": {"git_log": "feat: finished project"}}
    })
    prompt_res = json.loads(daemon.handle_request(prompt_req))
    assert "feat: finished project" in prompt_res["result"]["messages"][0]["content"]["text"]

def test_daemon_path_sanitization():
    daemon = PersonalMCPDaemon(":memory:", sandbox_root="/tmp/sandbox")
    with pytest.raises(PermissionError) as exc:
        daemon.validate_path("../../etc/shadow")
    assert "Path Traversal Blocked" in str(exc.value)

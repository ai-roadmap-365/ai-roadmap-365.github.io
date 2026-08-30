import pytest
import tempfile
import os
from examples.mcp_security_guard import MCPSecurityGuard

def test_path_sanitization_valid():
    with tempfile.TemporaryDirectory() as tmpdir:
        guard = MCPSecurityGuard(tmpdir)
        valid_path = guard.validate_path("subfolder/data.txt")
        assert valid_path.startswith(os.path.realpath(tmpdir))

def test_path_traversal_rejection():
    with tempfile.TemporaryDirectory() as tmpdir:
        guard = MCPSecurityGuard(tmpdir)
        with pytest.raises(PermissionError) as exc:
            guard.validate_path("../../etc/passwd")
        assert "Path Traversal Blocked" in str(exc.value)

def test_destructive_tool_blocked_without_approval():
    guard = MCPSecurityGuard("/tmp")
    res = guard.authorize_and_execute("delete_file", {"target": "data.db"}, lambda a: "Deleted", human_approved=False)
    assert res["isError"] is True
    assert "requires human approval" in res["content"][0]["text"]
    assert guard.audit_log[-1]["status"] == "BLOCKED_AWAITING_APPROVAL"

def test_destructive_tool_executed_with_approval():
    guard = MCPSecurityGuard("/tmp")
    res = guard.authorize_and_execute("delete_file", {"target": "data.db"}, lambda a: "Deleted", human_approved=True)
    assert res["isError"] is False
    assert res["content"][0]["text"] == "Deleted"
    assert guard.audit_log[-1]["status"] == "SUCCESS"

def test_safe_read_tool_auto_approved():
    guard = MCPSecurityGuard("/tmp")
    res = guard.authorize_and_execute("read_data", {"key": 1}, lambda a: "Value 1")
    assert res["isError"] is False
    assert res["content"][0]["text"] == "Value 1"

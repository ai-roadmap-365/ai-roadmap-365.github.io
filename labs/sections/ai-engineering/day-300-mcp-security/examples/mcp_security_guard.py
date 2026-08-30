import os
from typing import Dict, Any, Callable, List

class MCPSecurityGuard:
    def __init__(self, sandbox_root: str):
        self.sandbox_root = os.path.realpath(sandbox_root)
        self.destructive_tools = {"delete_file", "drop_table", "execute_shell"}
        self.audit_log: List[Dict[str, Any]] = []
        
    def validate_path(self, relative_path: str) -> str:
        target = os.path.realpath(os.path.join(self.sandbox_root, relative_path))
        if os.path.commonpath([target, self.sandbox_root]) != self.sandbox_root:
            raise PermissionError(f"Path Traversal Blocked: '{relative_path}' escapes sandbox.")
        return target
        
    def authorize_and_execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        handler_fn: Callable,
        human_approved: bool = False
    ) -> Dict[str, Any]:
        is_destructive = tool_name in self.destructive_tools
        
        if is_destructive and not human_approved:
            self.audit_log.append({
                "tool": tool_name,
                "status": "BLOCKED_AWAITING_APPROVAL",
                "arguments": arguments
            })
            return {
                "content": [{"type": "text", "text": f"Execution blocked: Tool '{tool_name}' requires human approval."}],
                "isError": True
            }
            
        try:
            result = handler_fn(arguments)
            self.audit_log.append({
                "tool": tool_name,
                "status": "SUCCESS",
                "arguments": arguments
            })
            return {
                "content": [{"type": "text", "text": str(result)}],
                "isError": False
            }
        except Exception as e:
            self.audit_log.append({
                "tool": tool_name,
                "status": "ERROR",
                "error": str(e)
            })
            return {
                "content": [{"type": "text", "text": f"Runtime Security Error: {str(e)}"}],
                "isError": True
            }

if __name__ == "__main__":
    guard = MCPSecurityGuard("/tmp/mcp_sandbox")
    print("Sandbox root:", guard.sandbox_root)
    # Test safe execution
    res = guard.authorize_and_execute("read_file", {"path": "safe.txt"}, lambda a: "File data")
    print("Safe read result:", res)

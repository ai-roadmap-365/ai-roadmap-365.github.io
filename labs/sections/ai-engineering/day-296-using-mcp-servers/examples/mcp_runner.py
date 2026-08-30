import json
import os
import sys
from typing import Dict, Any, List, Optional

class MCPConfigParser:
    @staticmethod
    def parse_config(config_json: str) -> Dict[str, Any]:
        data = json.loads(config_json)
        if "mcpServers" not in data or not isinstance(data["mcpServers"], dict):
            raise ValueError("Invalid configuration: missing 'mcpServers' object.")
        return data["mcpServers"]

class MockMCPServerProcess:
    """In-memory mock representing a subprocess stdio pipe for testing."""
    def __init__(self, name: str = "mock-server"):
        self.name = name
        self.tools = {
            "get_status": lambda args: {"status": "ONLINE", "uptime_sec": 4200}
        }
        
    def process_line(self, line: str) -> Optional[str]:
        msg = json.loads(line.strip())
        method = msg.get("method")
        msg_id = msg.get("id")
        
        if method == "initialize":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": self.name, "version": "1.0.0"}
                }
            })
        elif method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [{
                        "name": "get_status",
                        "description": "Get server health status",
                        "inputSchema": {"type": "object"}
                    }]
                }
            })
        elif method == "tools/call":
            params = msg.get("params", {})
            tool_name = params.get("name")
            if tool_name in self.tools:
                res = self.tools[tool_name](params.get("arguments", {}))
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(res)}],
                        "isError": False
                    }
                })
        return None

class LocalMCPRunner:
    def __init__(self, server_name: str, config: Dict[str, Any]):
        self.server_name = server_name
        self.config = config
        self.mock_proc = MockMCPServerProcess(server_name)
        self.request_id = 0
        
    def initialize(self) -> Dict[str, Any]:
        self.request_id += 1
        req = json.dumps({"jsonrpc": "2.0", "id": self.request_id, "method": "initialize"})
        resp = self.mock_proc.process_line(req)
        return json.loads(resp)
        
    def list_tools(self) -> List[Dict[str, Any]]:
        self.request_id += 1
        req = json.dumps({"jsonrpc": "2.0", "id": self.request_id, "method": "tools/list"})
        resp = self.mock_proc.process_line(req)
        return json.loads(resp)["result"]["tools"]
        
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        self.request_id += 1
        req = json.dumps({
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments}
        })
        resp = self.mock_proc.process_line(req)
        return json.loads(resp)["result"]

if __name__ == "__main__":
    runner = LocalMCPRunner("test-srv", {"command": "python", "args": []})
    init_res = runner.initialize()
    print("Initialized:", init_res["result"]["serverInfo"])
    tools = runner.list_tools()
    print("Tools:", tools)
    call_res = runner.call_tool("get_status", {})
    print("Call result:", call_res["content"][0]["text"])

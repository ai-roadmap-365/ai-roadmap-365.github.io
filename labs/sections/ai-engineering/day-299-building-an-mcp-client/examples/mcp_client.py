import json
from typing import Dict, Any, List, Optional

class MockMCPServerInstance:
    def __init__(self, name: str, tools_dict: Dict[str, Any]):
        self.name = name
        self.tools_dict = tools_dict
        
    def handle_line(self, line: str) -> Optional[str]:
        msg = json.loads(line.strip())
        method = msg.get("method")
        msg_id = msg.get("id")
        
        if method == "initialize":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"protocolVersion": "2024-11-05", "serverInfo": {"name": self.name}}
            })
        elif method == "tools/list":
            tool_list = [
                {"name": name, "description": f"Tool {name}", "inputSchema": {"type": "object"}}
                for name in self.tools_dict
            ]
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": tool_list}})
        elif method == "tools/call":
            params = msg.get("params", {})
            tool_name = params.get("name")
            if tool_name in self.tools_dict:
                handler = self.tools_dict[tool_name]
                res = handler(params.get("arguments", {}))
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": str(res)}], "isError": False}
                })
        return None

class AutonomousMCPAgent:
    def __init__(self):
        self.servers: Dict[str, MockMCPServerInstance] = {}
        self.tool_routing: Dict[str, MockMCPServerInstance] = {}
        self.unified_tools: List[Dict[str, Any]] = []
        self.req_id = 0
        
    def register_server(self, name: str, server_instance: MockMCPServerInstance):
        self.servers[name] = server_instance
        # Handshake
        self.req_id += 1
        init_req = json.dumps({"jsonrpc": "2.0", "id": self.req_id, "method": "initialize"})
        server_instance.handle_line(init_req)
        
        # Tools list
        self.req_id += 1
        list_req = json.dumps({"jsonrpc": "2.0", "id": self.req_id, "method": "tools/list"})
        list_resp = json.loads(server_instance.handle_line(list_req))
        
        tools = list_resp.get("result", {}).get("tools", [])
        for t in tools:
            self.tool_routing[t["name"]] = server_instance
            self.unified_tools.append(t)
            
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        if tool_name not in self.tool_routing:
            return f"Error: Tool '{tool_name}' not found."
        server = self.tool_routing[tool_name]
        self.req_id += 1
        call_req = json.dumps({
            "jsonrpc": "2.0",
            "id": self.req_id,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments}
        })
        resp = json.loads(server.handle_line(call_req))
        content = resp.get("result", {}).get("content", [])
        return content[0]["text"] if content else ""

if __name__ == "__main__":
    agent = AutonomousMCPAgent()
    srv1 = MockMCPServerInstance("db-srv", {"query_users": lambda args: "Alice, Bob"})
    srv2 = MockMCPServerInstance("fs-srv", {"read_file": lambda args: "File contents: OK"})
    agent.register_server("db-srv", srv1)
    agent.register_server("fs-srv", srv2)
    print("Unified tools:", [t["name"] for t in agent.unified_tools])
    print("DB Result:", agent.execute_tool("query_users", {}))
    print("FS Result:", agent.execute_tool("read_file", {}))

import json
from typing import Dict, Any, Optional

class MCPProtocolHandler:
    def __init__(self, server_name: str = "demo-server", server_version: str = "1.0.0"):
        self.server_name = server_name
        self.server_version = server_version
        self.tools: Dict[str, Dict[str, Any]] = {}
        
    def register_tool(self, name: str, description: str, input_schema: Dict[str, Any], handler_fn):
        self.tools[name] = {
            "definition": {
                "name": name,
                "description": description,
                "inputSchema": input_schema
            },
            "handler": handler_fn
        }
        
    def handle_message(self, raw_message: str) -> Optional[str]:
        try:
            msg = json.loads(raw_message.strip())
        except Exception:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            })
            
        method = msg.get("method")
        msg_id = msg.get("id")
        
        if method == "initialize":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": False}
                    },
                    "serverInfo": {
                        "name": self.server_name,
                        "version": self.server_version
                    }
                }
            })
            
        elif method == "notifications/initialized":
            return None
            
        elif method == "tools/list":
            tool_list = [t["definition"] for t in self.tools.values()]
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": tool_list
                }
            })
            
        elif method == "tools/call":
            params = msg.get("params", {})
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if tool_name not in self.tools:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
                })
                
            try:
                handler = self.tools[tool_name]["handler"]
                result_text = handler(tool_args)
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": str(result_text)}
                        ],
                        "isError": False
                    }
                })
            except Exception as e:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": f"Execution error: {str(e)}"}
                        ],
                        "isError": True
                    }
                })
                
        if msg_id is not None:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            })
        return None

if __name__ == "__main__":
    server = MCPProtocolHandler("math-server", "1.0.0")
    server.register_tool(
        "add", 
        "Add two numbers", 
        {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}},
        lambda args: args["a"] + args["b"]
    )
    resp = server.handle_message('{"jsonrpc": "2.0", "id": 1, "method": "initialize"}')
    print("Init response:", resp)

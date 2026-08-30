import inspect
import json
from typing import Dict, Any, Callable, get_type_hints, List, Optional

class CustomMCPServer:
    def __init__(self, name: str = "custom-mcp-server"):
        self.name = name
        self.tools: Dict[str, Dict[str, Any]] = {}
        
    def tool(self, name: Optional[str] = None, description: Optional[str] = None):
        def decorator(fn: Callable):
            tool_name = name or fn.__name__
            tool_desc = description or (inspect.getdoc(fn) or "No description provided.")
            
            sig = inspect.signature(fn)
            type_hints = get_type_hints(fn)
            
            properties = {}
            required = []
            
            for param_name, param in sig.parameters.items():
                p_type = type_hints.get(param_name, str)
                json_type = "string"
                if p_type == int:
                    json_type = "integer"
                elif p_type == float:
                    json_type = "number"
                elif p_type == bool:
                    json_type = "boolean"
                elif p_type == list:
                    json_type = "array"
                    
                properties[param_name] = {"type": json_type}
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)
                    
            input_schema = {
                "type": "object",
                "properties": properties,
                "required": required
            }
            
            self.tools[tool_name] = {
                "name": tool_name,
                "description": tool_desc,
                "inputSchema": input_schema,
                "handler": fn
            }
            return fn
        return decorator
        
    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "inputSchema": t["inputSchema"]
            }
            for t in self.tools.values()
        ]
        
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.tools:
            return {
                "content": [{"type": "text", "text": f"Tool '{name}' not found."}],
                "isError": True
            }
            
        tool = self.tools[name]
        fn = tool["handler"]
        
        try:
            res = fn(**arguments)
            return {
                "content": [{"type": "text", "text": str(res)}],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error executing {name}: {str(e)}"}],
                "isError": True
            }

if __name__ == "__main__":
    server = CustomMCPServer("retail-tools")
    
    @server.tool()
    def calculate_tax(amount: float, rate: float = 0.08) -> float:
        """Calculate total amount including tax."""
        return amount * (1.0 + rate)
        
    print("Registered tools:", server.list_tools())
    res = server.call_tool("calculate_tax", {"amount": 100.0, "rate": 0.10})
    print("Execution result:", res)

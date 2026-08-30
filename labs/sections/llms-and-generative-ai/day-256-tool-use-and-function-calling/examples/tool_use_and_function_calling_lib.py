from typing import Dict, Any, List, Callable
import json

def calculate_tax(amount: float, state: str = "CA") -> float:
    rate = 0.0725 if state == "CA" else 0.05
    return round(amount * (1 + rate), 2)

def get_order_status(order_id: str) -> str:
    orders = {"ORD-101": "Shipped", "ORD-102": "Processing"}
    return orders.get(order_id, "Order not found")

class ToolDispatcher:
    def __init__(self):
        self.registry: Dict[str, Callable] = {}
        self.schemas: List[Dict[str, Any]] = []

    def register_tool(self, name: str, description: str, schema: Dict[str, Any], func: Callable):
        self.registry[name] = func
        self.schemas.append({
            "name": name,
            "description": description,
            "input_schema": schema
        })

    def execute_tool(self, name: str, args: Dict[str, Any]) -> str:
        if name not in self.registry:
            return f"Error: Tool '{name}' is not registered."
        try:
            return str(self.registry[name](**args))
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"

    def run_agent_turn(self, mock_model_response: Dict[str, Any]) -> Dict[str, Any]:
        tool_results = []
        if mock_model_response.get("stop_reason") == "tool_use":
            for call in mock_model_response.get("content", []):
                if call.get("type") == "tool_use":
                    out = self.execute_tool(call["name"], call["input"])
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": call["id"],
                        "content": out
                    })
        return {
            "tool_results": tool_results,
            "is_complete": len(tool_results) == 0
        }

def run_dispatcher_demo():
    dispatcher = ToolDispatcher()
    dispatcher.register_tool(
        "calculate_tax",
        "Calculates tax for an amount and state",
        {"type": "object", "properties": {"amount": {"type": "number"}, "state": {"type": "string"}}},
        calculate_tax
    )

    mock_response = {
        "stop_reason": "tool_use",
        "content": [{
            "type": "tool_use",
            "id": "toolu_tax_01",
            "name": "calculate_tax",
            "input": {"amount": 100.0, "state": "CA"}
        }]
    }

    result = dispatcher.run_agent_turn(mock_response)
    print("Dispatcher Demo Executed. Result:", result["tool_results"][0]["content"])
    return result

if __name__ == "__main__":
    run_dispatcher_demo()

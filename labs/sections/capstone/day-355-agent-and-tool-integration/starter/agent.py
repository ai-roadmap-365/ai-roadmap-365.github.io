import json
from typing import Dict, Any, List, Callable, Tuple

class ToolDefinition:
    def __init__(self, name: str, description: str, parameters_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters_schema = parameters_schema

class AgentCheckpoint:
    def __init__(self, turn: int, thought: str, action: str, action_input: Dict[str, Any], observation: str):
        self.turn = turn
        self.thought = thought
        self.action = action
        self.action_input = action_input
        self.observation = observation

    def model_dump(self) -> Dict[str, Any]:
        return {
            "turn": self.turn,
            "thought": self.thought,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self.observation
        }

class AgentOrchestrator:
    def __init__(self, model_fn: Callable[[str], str], max_turns: int = 5):
        self.model_fn = model_fn
        self.max_turns = max_turns
        self.tool_registry: Dict[str, Tuple[ToolDefinition, Callable]] = {}
        self.checkpoints: List[AgentCheckpoint] = []

    def register_tool(self, name: str, description: str, param_schema: Dict[str, Any], handler: Callable):
        tool_def = ToolDefinition(name=name, description=description, parameters_schema=param_schema)
        self.tool_registry[name] = (tool_def, handler)

    def _execute_sandboxed_tool(self, name: str, args: Dict[str, Any]) -> str:
        if name not in self.tool_registry:
            return f"ERROR: Tool '{name}' not found in registry."
        
        _, handler = self.tool_registry[name]
        try:
            result = handler(**args)
            return json.dumps(result) if isinstance(result, (dict, list)) else str(result)
        except Exception as e:
            return f"ERROR executing tool '{name}': {str(e)}"

    def run_agent(self, user_goal: str) -> Dict[str, Any]:
        scratchpad = f"User Goal: {user_goal}\n"
        self.checkpoints = []

        for turn in range(1, self.max_turns + 1):
            tools_desc = "\n".join([f"- {t.name}: {t.description}" for t, _ in self.tool_registry.values()])
            prompt = (
                f"You are an autonomous AI agent. Available tools:\n{tools_desc}\n\n"
                f"Scratchpad:\n{scratchpad}\n\n"
                f"Emit JSON with 'thought', 'action' (tool name or 'FINAL_ANSWER'), and 'action_input'."
            )

            raw_resp = self.model_fn(prompt)
            try:
                cleaned = raw_resp.strip().removeprefix("```json").removesuffix("```").strip()
                action_payload = json.loads(cleaned)
                thought = action_payload.get("thought", "")
                action = action_payload.get("action", "")
                action_input = action_payload.get("action_input", {})
            except Exception:
                thought = "Parse error"
                action = "FINAL_ANSWER"
                action_input = {"answer": raw_resp}

            if action == "FINAL_ANSWER":
                self.checkpoints.append(AgentCheckpoint(
                    turn=turn, thought=thought, action="FINAL_ANSWER",
                    action_input=action_input, observation="COMPLETED"
                ))
                return {
                    "status": "SUCCESS",
                    "total_turns": turn,
                    "final_answer": action_input.get("answer", raw_resp),
                    "checkpoints": [c.model_dump() for c in self.checkpoints]
                }

            observation = self._execute_sandboxed_tool(action, action_input)
            scratchpad += f"\nTurn {turn}:\nThought: {thought}\nAction: {action}({action_input})\nObservation: {observation}\n"

            self.checkpoints.append(AgentCheckpoint(
                turn=turn, thought=thought, action=action,
                action_input=action_input, observation=observation
            ))

        return {
            "status": "MAX_TURNS_EXCEEDED",
            "total_turns": self.max_turns,
            "final_answer": "Agent reached maximum recursion depth without finishing.",
            "checkpoints": [c.model_dump() for c in self.checkpoints]
        }

if __name__ == "__main__":
    def mock_db(account_id: str): return {"balance": 15000}
    agent = AgentOrchestrator(model_fn=lambda p: '{"thought": "done", "action": "FINAL_ANSWER", "action_input": {"answer": "15000"}}')
    agent.register_tool("get_balance", "Get account balance", {}, mock_db)
    print(agent.run_agent("Check balance"))

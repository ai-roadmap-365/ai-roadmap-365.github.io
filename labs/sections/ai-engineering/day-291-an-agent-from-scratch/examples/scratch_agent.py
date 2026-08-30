import re
import json
from typing import Dict, Any, List, Optional, Tuple, Callable

class PurePythonAgent:
    def __init__(self, max_steps: int = 8, window_size: int = 4):
        self.max_steps = max_steps
        self.window_size = window_size
        self.memory_store: Dict[str, str] = {}
        self.tools: Dict[str, Callable] = {
            "calculator": self._tool_calculator,
            "set_memory": self._tool_set_memory,
            "get_memory": self._tool_get_memory,
            "search_kb": self._tool_search_kb
        }
        self.trajectory: List[Dict[str, str]] = []
        
    def _tool_calculator(self, expr: str) -> str:
        try:
            return str(eval(expr, {"__builtins__": None}, {}))
        except Exception as e:
            return f"Math Error: {str(e)}"
            
    def _tool_set_memory(self, key: str, value: str) -> str:
        self.memory_store[key] = value
        return f"Stored '{key}' = '{value}'"
        
    def _tool_get_memory(self, key: str) -> str:
        return self.memory_store.get(key, f"Key '{key}' not found.")
        
    def _tool_search_kb(self, query: str) -> str:
        kb = {
            "project mars": "Project Mars budget is $450 million with 12 milestones.",
            "team alpha": "Team Alpha has 15 core engineers and 4 researchers."
        }
        for k, v in kb.items():
            if k in query.lower():
                return v
        return "No matching records found in knowledge base."
        
    def render_prompt(self, goal: str) -> str:
        lines = [
            "SYSTEM: You are an autonomous AI agent.",
            f"GOAL: {goal}",
            "--- SCRATCHPAD ---"
        ]
        
        # Apply sliding window over trajectory
        if len(self.trajectory) > self.window_size:
            truncated_count = len(self.trajectory) - self.window_size
            lines.append(f"[System Notice: {truncated_count} earlier steps compacted]")
            active_steps = self.trajectory[-self.window_size:]
        else:
            active_steps = self.trajectory
            
        for step in active_steps:
            lines.append(f"{step['type'].capitalize()}: {step['content']}")
            
        return "\n".join(lines)
        
    def parse_step(self, text: str) -> Tuple[str, str, Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|\nFinal Answer:|$)", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else ""
        
        if "Final Answer:" in text:
            ans_match = re.search(r"Final Answer:\s*(.*)", text, re.DOTALL)
            return "FINAL", thought, None, None, ans_match.group(1).strip() if ans_match else text.strip()
            
        action_match = re.search(r"Action:\s*([a-zA-Z0-9_]+)\s*\((.*)\)", text, re.DOTALL)
        if action_match:
            tool_name = action_match.group(1).strip()
            args_raw = action_match.group(2).strip()
            try:
                args = json.loads(args_raw) if args_raw else {}
                return "ACTION", thought, tool_name, args, None
            except json.JSONDecodeError as err:
                return "SYNTAX_ERROR", thought, tool_name, {"raw": args_raw, "error": str(err)}, None
                
        return "UNKNOWN", thought, None, None, None
        
    def step(self, mock_llm_output: str) -> Dict[str, Any]:
        stype, thought, tool, args, ans = self.parse_step(mock_llm_output)
        
        if stype == "FINAL":
            self.trajectory.append({"type": "thought", "content": thought})
            self.trajectory.append({"type": "final answer", "content": ans})
            return {"status": "COMPLETE", "final_answer": ans}
            
        elif stype == "ACTION":
            self.trajectory.append({"type": "thought", "content": thought})
            self.trajectory.append({"type": "action", "content": f"{tool}({json.dumps(args)})"})
            
            if tool in self.tools:
                obs = self.tools[tool](**args)
            else:
                obs = f"Error: Tool '{tool}' does not exist."
                
            self.trajectory.append({"type": "observation", "content": obs})
            return {"status": "CONTINUE", "observation": obs}
            
        elif stype == "SYNTAX_ERROR":
            self.trajectory.append({"type": "thought", "content": thought})
            obs = f"JSON parse error: {args['error']}. Please re-emit with valid JSON."
            self.trajectory.append({"type": "observation", "content": obs})
            return {"status": "CONTINUE", "observation": obs}
            
        else:
            obs = "Format error. Expected Action or Final Answer."
            self.trajectory.append({"type": "observation", "content": obs})
            return {"status": "CONTINUE", "observation": obs}

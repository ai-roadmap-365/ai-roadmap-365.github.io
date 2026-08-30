import re
import json
from typing import Dict, Any, Tuple, Optional, Callable

class ReActEngine:
    def __init__(self, tools: Optional[Dict[str, Callable]] = None, max_iterations: int = 6):
        self.tools = tools or {}
        self.max_iterations = max_iterations
        self.scratchpad: list = []
        
    def register_tool(self, name: str, func: Callable):
        self.tools[name] = func
        
    def parse_generation(self, text: str) -> Tuple[str, str, Optional[Dict[str, Any]], Optional[str]]:
        # Extract Thought
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|\nFinal Answer:|$)", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else ""
        
        # Check for Final Answer
        if "Final Answer:" in text:
            final_match = re.search(r"Final Answer:\s*(.*)", text, re.DOTALL)
            final_answer = final_match.group(1).strip() if final_match else text.strip()
            return "FINAL", thought, None, final_answer
            
        # Extract Action
        action_match = re.search(r"Action:\s*([a-zA-Z0-9_]+)\s*\((.*)\)", text, re.DOTALL)
        if action_match:
            tool_name = action_match.group(1).strip()
            args_raw = action_match.group(2).strip()
            try:
                args = json.loads(args_raw) if args_raw else {}
                return "ACTION", thought, {"tool": tool_name, "args": args}, None
            except json.JSONDecodeError as err:
                return "SYNTAX_ERROR", thought, {"tool": tool_name, "raw": args_raw, "error": str(err)}, None
                
        return "UNKNOWN", thought, None, None
        
    def execute_step(self, mock_llm_response: str) -> Dict[str, Any]:
        step_type, thought, action_data, final_ans = self.parse_generation(mock_llm_response)
        
        if step_type == "FINAL":
            self.scratchpad.append(f"Thought: {thought}\nFinal Answer: {final_ans}")
            return {"status": "COMPLETE", "final_answer": final_ans, "thought": thought}
            
        elif step_type == "ACTION":
            tool = action_data["tool"]
            args = action_data["args"]
            if tool in self.tools:
                try:
                    res = self.tools[tool](**args)
                    obs = f"Observation: {res}"
                except Exception as e:
                    obs = f"Observation: Error executing tool '{tool}': {str(e)}"
            else:
                obs = f"Observation: Tool '{tool}' does not exist in registry."
                
            self.scratchpad.append(f"Thought: {thought}\nAction: {tool}({json.dumps(args)})\n{obs}")
            return {"status": "CONTINUE", "thought": thought, "tool": tool, "observation": obs}
            
        elif step_type == "SYNTAX_ERROR":
            obs = f"Observation: JSON parse error in action parameters: {action_data['error']}. Please re-emit with valid JSON."
            self.scratchpad.append(f"Thought: {thought}\nAction: {action_data['tool']}({action_data['raw']})\n{obs}")
            return {"status": "CONTINUE", "thought": thought, "observation": obs}
            
        else:
            obs = "Observation: Format error. Expected 'Action: tool_name(args)' or 'Final Answer: answer'."
            self.scratchpad.append(f"Thought: {thought}\n{obs}")
            return {"status": "CONTINUE", "thought": thought, "observation": obs}

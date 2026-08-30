from enum import Enum
from typing import Dict, Any, List, Optional, Callable
import json

class AgentState(Enum):
    IDLE = "IDLE"
    THINKING = "THINKING"
    TOOL_CALL = "TOOL_CALL"
    OBSERVING = "OBSERVING"
    FINAL_ANSWER = "FINAL_ANSWER"
    MAX_STEPS_EXCEEDED = "MAX_STEPS_EXCEEDED"
    CYCLE_DETECTED = "CYCLE_DETECTED"
    ERROR = "ERROR"

class AgentTrajectory:
    def __init__(self):
        self.steps: List[Dict[str, Any]] = []
        
    def add_step(self, step_type: str, content: str, metadata: Optional[Dict] = None):
        self.steps.append({
            "step": len(self.steps) + 1,
            "type": step_type,
            "content": content,
            "metadata": metadata or {}
        })
        
    def get_scratchpad(self) -> str:
        lines = []
        for s in self.steps:
            lines.append(f"[{s['type'].upper()}]: {s['content']}")
        return "\n".join(lines)

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable[[str], str]] = {}
        
    def register(self, name: str, func: Callable[[str], str]):
        self._tools[name] = func
        
    def execute(self, name: str, arg: str) -> str:
        if name not in self._tools:
            return f"Error: Tool '{name}' not found in registry."
        try:
            return self._tools[name](arg)
        except Exception as e:
            return f"Error executing '{name}': {str(e)}"

class AgentRuntime:
    def __init__(self, tool_registry: ToolRegistry, max_steps: int = 5):
        self.state = AgentState.IDLE
        self.tools = tool_registry
        self.max_steps = max_steps
        self.trajectory = AgentTrajectory()
        self.transition_history: List[AgentState] = []
        
    def _set_state(self, new_state: AgentState):
        self.state = new_state
        self.transition_history.append(new_state)
        
    def step_loop(self, goal: str, mock_decisions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        self._set_state(AgentState.THINKING)
        self.trajectory.add_step("goal", goal)
        step_count = 0
        dec_idx = 0
        last_action = None
        
        while self.state not in (AgentState.FINAL_ANSWER, AgentState.MAX_STEPS_EXCEEDED, AgentState.CYCLE_DETECTED, AgentState.ERROR):
            step_count += 1
            if step_count > self.max_steps:
                self._set_state(AgentState.MAX_STEPS_EXCEEDED)
                self.trajectory.add_step("system", "Max steps budget exceeded.")
                break
                
            # Fetch decision (either from scripted mock decisions or heuristic fallback)
            if mock_decisions and dec_idx < len(mock_decisions):
                decision = mock_decisions[dec_idx]
                dec_idx += 1
            else:
                decision = {"type": "final_answer", "content": f"Completed objective: {goal}"}
                
            if decision["type"] == "tool_call":
                current_action = f"{decision['tool']}:{decision.get('args', '')}"
                if current_action == last_action:
                    self._set_state(AgentState.CYCLE_DETECTED)
                    self.trajectory.add_step("system", f"Cycle detected for action: {current_action}")
                    break
                last_action = current_action
                
                self._set_state(AgentState.TOOL_CALL)
                self.trajectory.add_step("thought", decision.get("thought", "Executing tool."))
                self.trajectory.add_step("action", json.dumps({"tool": decision["tool"], "args": decision.get("args", "")}))
                
                # Execute tool
                self._set_state(AgentState.OBSERVING)
                obs = self.tools.execute(decision["tool"], decision.get("args", ""))
                self.trajectory.add_step("observation", obs)
                
                # Re-enter thinking state
                self._set_state(AgentState.THINKING)
                
            elif decision["type"] == "final_answer":
                self._set_state(AgentState.FINAL_ANSWER)
                self.trajectory.add_step("final_answer", decision["content"])
                break
            else:
                self._set_state(AgentState.ERROR)
                self.trajectory.add_step("error", f"Unknown decision type: {decision['type']}")
                break
                
        return {
            "final_state": self.state.value,
            "step_count": step_count,
            "transitions": [s.value for s in self.transition_history],
            "scratchpad": self.trajectory.get_scratchpad()
        }

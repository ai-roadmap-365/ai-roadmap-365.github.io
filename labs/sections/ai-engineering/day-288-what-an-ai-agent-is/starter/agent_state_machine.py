"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Callable
import json

class AgentState(Enum):
    IDLE = 'IDLE'
    THINKING = 'THINKING'
    TOOL_CALL = 'TOOL_CALL'
    OBSERVING = 'OBSERVING'
    FINAL_ANSWER = 'FINAL_ANSWER'
    MAX_STEPS_EXCEEDED = 'MAX_STEPS_EXCEEDED'
    CYCLE_DETECTED = 'CYCLE_DETECTED'
    ERROR = 'ERROR'

class AgentTrajectory:

    def __init__(self):
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, step_type: str, content: str, metadata: Optional[Dict]=None):
        raise NotImplementedError('TASK 1: implement add_step.')

    def get_scratchpad(self) -> str:
        raise NotImplementedError('TASK 2: implement get_scratchpad.')

class ToolRegistry:

    def __init__(self):
        self._tools: Dict[str, Callable[[str], str]] = {}

    def register(self, name: str, func: Callable[[str], str]):
        raise NotImplementedError('TASK 3: implement register.')

    def execute(self, name: str, arg: str) -> str:
        raise NotImplementedError('TASK 4: implement execute.')

class AgentRuntime:

    def __init__(self, tool_registry: ToolRegistry, max_steps: int=5):
        self.state = AgentState.IDLE
        self.tools = tool_registry
        self.max_steps = max_steps
        self.trajectory = AgentTrajectory()
        self.transition_history: List[AgentState] = []

    def _set_state(self, new_state: AgentState):
        raise NotImplementedError('TASK 5: implement _set_state.')

    def step_loop(self, goal: str, mock_decisions: Optional[List[Dict[str, Any]]]=None) -> Dict[str, Any]:
        raise NotImplementedError('TASK 6: implement step_loop.')

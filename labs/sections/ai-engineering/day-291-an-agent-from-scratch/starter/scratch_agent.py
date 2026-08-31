"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple, Callable

class PurePythonAgent:

    def __init__(self, max_steps: int=8, window_size: int=4):
        self.max_steps = max_steps
        self.window_size = window_size
        self.memory_store: Dict[str, str] = {}
        self.tools: Dict[str, Callable] = {'calculator': self._tool_calculator, 'set_memory': self._tool_set_memory, 'get_memory': self._tool_get_memory, 'search_kb': self._tool_search_kb}
        self.trajectory: List[Dict[str, str]] = []

    def _tool_calculator(self, expr: str) -> str:
        raise NotImplementedError('TASK 1: implement _tool_calculator.')

    def _tool_set_memory(self, key: str, value: str) -> str:
        raise NotImplementedError('TASK 2: implement _tool_set_memory.')

    def _tool_get_memory(self, key: str) -> str:
        raise NotImplementedError('TASK 3: implement _tool_get_memory.')

    def _tool_search_kb(self, query: str) -> str:
        raise NotImplementedError('TASK 4: implement _tool_search_kb.')

    def render_prompt(self, goal: str) -> str:
        raise NotImplementedError('TASK 5: implement render_prompt.')

    def parse_step(self, text: str) -> Tuple[str, str, Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        raise NotImplementedError('TASK 6: implement parse_step.')

    def step(self, mock_llm_output: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 7: implement step.')

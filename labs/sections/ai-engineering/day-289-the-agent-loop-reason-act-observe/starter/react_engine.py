"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import re
import json
from typing import Dict, Any, Tuple, Optional, Callable

class ReActEngine:

    def __init__(self, tools: Optional[Dict[str, Callable]]=None, max_iterations: int=6):
        self.tools = tools or {}
        self.max_iterations = max_iterations
        self.scratchpad: list = []

    def register_tool(self, name: str, func: Callable):
        raise NotImplementedError('TASK 1: implement register_tool.')

    def parse_generation(self, text: str) -> Tuple[str, str, Optional[Dict[str, Any]], Optional[str]]:
        raise NotImplementedError('TASK 2: implement parse_generation.')

    def execute_step(self, mock_llm_response: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 3: implement execute_step.')

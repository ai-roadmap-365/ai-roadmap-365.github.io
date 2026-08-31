"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import time
import uuid
import json
from typing import Dict, Any, List, Optional

class Span:

    def __init__(self, name: str, kind: str, parent_id: Optional[str]=None):
        self.span_id = str(uuid.uuid4())[:8]
        self.parent_id = parent_id
        self.name = name
        self.kind = kind
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.duration_ms: float = 0.0
        self.attributes: Dict[str, Any] = {}
        self.children: List['Span'] = []

    def set_attribute(self, key: str, value: Any):
        raise NotImplementedError('TASK 1: implement set_attribute.')

    def finish(self):
        raise NotImplementedError('TASK 2: implement finish.')

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError('TASK 3: implement to_dict.')

class TraceTelemetryEngine:

    def __init__(self):
        self.traces: Dict[str, Span] = {}

    def start_trace(self, name: str) -> Span:
        raise NotImplementedError('TASK 4: implement start_trace.')

    def create_child_span(self, parent_span: Span, name: str, kind: str) -> Span:
        raise NotImplementedError('TASK 5: implement create_child_span.')

    @staticmethod
    def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str='claude-3-5-sonnet') -> float:
        raise NotImplementedError('TASK 6: implement calculate_cost.')
if __name__ == '__main__':
    engine = TraceTelemetryEngine()
    root = engine.start_trace('Test_Trace')
    root.finish()
    print('Trace Root:', root.to_dict())

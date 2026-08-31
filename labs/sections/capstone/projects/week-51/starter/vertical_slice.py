"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import json
import time
from typing import Dict, Any, List

class AnswerPayload:

    def __init__(self, summary: str, detailed_points: List[str], citations: List[str], confidence_score: float):
        self.summary = summary
        self.detailed_points = detailed_points
        self.citations = citations
        self.confidence_score = float(confidence_score)

    def model_dump(self) -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement model_dump.')

class CapstoneVerticalSlice:

    def __init__(self, model_fn=None):
        self.documents = [{'id': 'doc1', 'text': 'Enterprise SLA guarantees 99.9% uptime with 24/7 dedicated support.'}, {'id': 'doc2', 'text': 'Standard liability cap is fixed at $1,000,000 USD under Delaware governing law.'}]
        self.tools = {'calc_penalty': lambda base, rate: base * rate}
        self.model_fn = model_fn or self._default_model_fn

    def _default_model_fn(self, prompt: str) -> str:
        raise NotImplementedError('TASK 2: implement _default_model_fn.')

    def hybrid_retrieval(self, query: str) -> List[Dict[str, Any]]:
        raise NotImplementedError('TASK 3: implement hybrid_retrieval.')

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        raise NotImplementedError('TASK 4: implement execute_tool.')

    def run_query(self, user_query: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 5: implement run_query.')
if __name__ == '__main__':
    slice_app = CapstoneVerticalSlice()
    print(json.dumps(slice_app.run_query('What is SLA?'), indent=2))

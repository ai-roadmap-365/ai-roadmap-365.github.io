"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import json
import time
from typing import Dict, Any, List, Tuple

class AnswerPayload:

    def __init__(self, summary: str, detailed_points: List[str], citations: List[str], confidence_score: float):
        raise NotImplementedError('TASK 1: implement __init__.')

    def model_dump(self) -> Dict[str, Any]:
        raise NotImplementedError('TASK 2: implement model_dump.')

class CoreAIEngine:

    def __init__(self, primary_model_fn, fallback_model_fn=None, failure_threshold: int=3, timeout_seconds: float=2.5):
        self.primary_model_fn = primary_model_fn
        self.fallback_model_fn = fallback_model_fn
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.consecutive_failures = 0
        self.circuit_open = False

    def synthesize_prompt(self, user_query: str, context_chunks: List[Dict[str, Any]]) -> str:
        raise NotImplementedError('TASK 3: implement synthesize_prompt.')

    def execute_inference_with_fallback(self, prompt: str) -> Tuple[str, str]:
        raise NotImplementedError('TASK 4: implement execute_inference_with_fallback.')

    def parse_and_repair_json(self, raw_text: str, max_retries: int=1) -> AnswerPayload:
        raise NotImplementedError('TASK 5: implement parse_and_repair_json.')
if __name__ == '__main__':

    def mock_primary(p: str) -> str:
        raise NotImplementedError('TASK 6: implement mock_primary.')
    engine = CoreAIEngine(primary_model_fn=mock_primary)
    prompt = engine.synthesize_prompt('What is SLA?', [{'id': 'doc1', 'text': 'SLA is 99.9%.'}])
    raw, prov = engine.execute_inference_with_fallback(prompt)
    print('Parsed:', engine.parse_and_repair_json(raw).summary)

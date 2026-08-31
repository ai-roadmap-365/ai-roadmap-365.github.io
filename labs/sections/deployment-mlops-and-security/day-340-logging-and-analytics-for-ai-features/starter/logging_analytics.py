"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import re
import json
import uuid
import time
from typing import Dict, Any, List, Optional

class AIStructuredLoggingAnalyticsEngine:

    def __init__(self, prompt_cost_per_1k: float=0.002, completion_cost_per_1k: float=0.006):
        self.prompt_rate = prompt_cost_per_1k / 1000.0
        self.completion_rate = completion_cost_per_1k / 1000.0
        self.tenant_ledger: Dict[str, Dict[str, Any]] = {}
        self.emitted_logs: List[Dict[str, Any]] = []

    def sanitize_pii(self, text: str) -> str:
        raise NotImplementedError('TASK 1: implement sanitize_pii.')

    def log_inference_event(self, tenant_id: str, prompt: str, completion: str, prompt_tokens: int, completion_tokens: int, trace_id: Optional[str]=None) -> Dict[str, Any]:
        raise NotImplementedError('TASK 2: implement log_inference_event.')
if __name__ == '__main__':
    e = AIStructuredLoggingAnalyticsEngine()
    print(e.log_inference_event('t1', 'Email is test@example.com', 'OK', 100, 50))

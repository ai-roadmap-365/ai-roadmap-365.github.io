"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import time
import json
from typing import Dict, Any, List, Optional, Tuple

class ResilientLLMBackend:

    def __init__(self, failure_threshold: int=3, reset_timeout_seconds: float=1.0):
        self.failure_threshold = int(failure_threshold)
        self.reset_timeout = float(reset_timeout_seconds)
        self.state = 'CLOSED'
        self.failure_count = 0
        self.last_state_change = time.time()
        self.idempotency_store: Dict[str, Dict[str, Any]] = {}

    def record_failure(self):
        raise NotImplementedError('TASK 1: implement record_failure.')

    def record_success(self):
        raise NotImplementedError('TASK 2: implement record_success.')

    def check_circuit_state(self) -> str:
        raise NotImplementedError('TASK 3: implement check_circuit_state.')

    def process_request(self, idempotency_key: str, prompt: str, simulate_upstream_fail: bool=False) -> Dict[str, Any]:
        raise NotImplementedError('TASK 4: implement process_request.')
if __name__ == '__main__':
    backend = ResilientLLMBackend()
    print('Normal:', backend.process_request('k1', 'Hello'))

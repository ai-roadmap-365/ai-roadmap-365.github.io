"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import time
import json
from typing import Dict, Any, List, Tuple

class Milestone1AuditSuite:

    def __init__(self, max_latency_ms: float=1500.0, min_faithfulness: float=0.9):
        self.max_latency_ms = max_latency_ms
        self.min_faithfulness = min_faithfulness

    def profile_vertical_slice(self, mock_pipeline_fn) -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement profile_vertical_slice.')

    def audit_milestone(self, pipeline_fn, eval_metrics: Dict[str, float]) -> Dict[str, Any]:
        raise NotImplementedError('TASK 2: implement audit_milestone.')
if __name__ == '__main__':

    def sample_pipeline():
        raise NotImplementedError('TASK 3: implement sample_pipeline.')
    auditor = Milestone1AuditSuite()
    print(auditor.audit_milestone(sample_pipeline, {'faithfulness': 0.95}))

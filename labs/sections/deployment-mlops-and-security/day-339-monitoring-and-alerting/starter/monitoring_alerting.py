"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import numpy as np
import time
from typing import Dict, Any, List, Optional

class AIObservabilityAlertEngine:

    def __init__(self, p95_ttft_threshold_ms: float=300.0, error_rate_threshold_pct: float=1.0):
        self.ttft_threshold = float(p95_ttft_threshold_ms)
        self.error_threshold = float(error_rate_threshold_pct)
        self.ttft_samples: List[float] = []
        self.total_requests = 0
        self.total_errors = 0
        self.active_alerts: List[Dict[str, Any]] = []

    def record_inference_event(self, ttft_ms: float, is_error: bool=False):
        raise NotImplementedError('TASK 1: implement record_inference_event.')

    def evaluate_metrics(self) -> Dict[str, Any]:
        raise NotImplementedError('TASK 2: implement evaluate_metrics.')
if __name__ == '__main__':
    e = AIObservabilityAlertEngine()
    e.record_inference_event(100.0)
    print(e.evaluate_metrics())

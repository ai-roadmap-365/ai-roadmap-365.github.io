"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import math
import time
from typing import Dict, Any, List, Optional

class GPUAutoscalingDecisionEngine:

    def __init__(self, min_replicas: int=1, max_replicas: int=10, target_waiting_per_pod: int=5, scale_down_cooldown_seconds: int=300):
        self.min_replicas = int(min_replicas)
        self.max_replicas = int(max_replicas)
        self.target_per_pod = int(target_waiting_per_pod)
        self.cooldown_sec = int(scale_down_cooldown_seconds)
        self.current_replicas = int(min_replicas)
        self.idle_since_timestamp: Optional[float] = None

    def calculate_desired_replicas(self, waiting_requests: int, current_timestamp: float) -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement calculate_desired_replicas.')
if __name__ == '__main__':
    eng = GPUAutoscalingDecisionEngine(min_replicas=1, max_replicas=5, target_waiting_per_pod=5, scale_down_cooldown_seconds=10)
    print(eng.calculate_desired_replicas(20, 100.0))
    print(eng.calculate_desired_replicas(0, 102.0))
    print(eng.calculate_desired_replicas(0, 115.0))

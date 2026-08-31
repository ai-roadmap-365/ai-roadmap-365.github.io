"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import time
from typing import Dict, Any, List, Optional

class GPUServingInfrastructureSimulator:

    def __init__(self, max_batch_size: int=4, max_queue_delay_ms: float=5.0):
        self.max_batch = int(max_batch_size)
        self.max_delay_ms = float(max_queue_delay_ms)
        self.vram_pool_mb = 16384
        self.allocated_models: Dict[str, int] = {}
        self.incoming_queue: List[Dict[str, Any]] = []
        self.execution_log: List[Dict[str, Any]] = []

    def load_model_to_vram(self, model_name: str, required_vram_mb: int) -> bool:
        raise NotImplementedError('TASK 1: implement load_model_to_vram.')

    def enqueue_request(self, req_id: str, prompt: str, arrival_time: float):
        raise NotImplementedError('TASK 2: implement enqueue_request.')

    def process_dynamic_batch(self, current_time: float) -> Optional[Dict[str, Any]]:
        raise NotImplementedError('TASK 3: implement process_dynamic_batch.')
if __name__ == '__main__':
    s = GPUServingInfrastructureSimulator(2, 5.0)
    s.enqueue_request('r1', 'p1', 100.0)
    s.enqueue_request('r2', 'p2', 100.001)
    print(s.process_dynamic_batch(100.002))

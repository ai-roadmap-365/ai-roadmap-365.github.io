"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

from typing import Dict, Any, List, Optional
import math
import time

class PagedCache:

    def __init__(self, total_blocks: int=16, block_size: int=4):
        self.block_size = block_size
        self.free_blocks = list(range(total_blocks))
        self.tables: Dict[str, List[int]] = {}

    def allocate(self, req_id: str, tokens: int) -> bool:
        raise NotImplementedError('TASK 1: implement allocate.')

    def free(self, req_id: str):
        raise NotImplementedError('TASK 2: implement free.')

class ServingWorker:

    def __init__(self, worker_id: str, total_blocks: int=16):
        self.worker_id = worker_id
        self.cache = PagedCache(total_blocks=total_blocks)
        self.active_batch: List[Dict[str, Any]] = []
        self.is_healthy = True

    def add_request(self, req_id: str, prompt_tokens: int, max_tokens: int) -> bool:
        raise NotImplementedError('TASK 3: implement add_request.')

    def step(self) -> List[str]:
        raise NotImplementedError('TASK 4: implement step.')

class DeployedAISystem:

    def __init__(self, num_workers: int=2, failure_threshold: int=3):
        self.workers = [ServingWorker(f'worker_{i}') for i in range(num_workers)]
        self.failure_threshold = failure_threshold
        self.circuit_state = 'CLOSED'
        self.total_routed = 0

    def route_request(self, req_id: str, prompt_tokens: int, max_tokens: int) -> Dict[str, Any]:
        raise NotImplementedError('TASK 5: implement route_request.')

    def step_all(self) -> Dict[str, List[str]]:
        raise NotImplementedError('TASK 6: implement step_all.')
if __name__ == '__main__':
    sys = DeployedAISystem(num_workers=2)
    print('Route 1:', sys.route_request('r1', 4, 2))
    print('Route 2:', sys.route_request('r2', 4, 3))
    print('Step:', sys.step_all())

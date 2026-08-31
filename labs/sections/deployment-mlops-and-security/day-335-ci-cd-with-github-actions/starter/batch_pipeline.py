"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import time
from typing import Dict, Any, List, Optional

class DistributedBatchPipeline:

    def __init__(self, max_retries: int=3):
        self.max_retries = int(max_retries)
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_checkpoints: Dict[str, Any] = {}
        self.dead_letter_queue: List[Dict[str, Any]] = []

    def enqueue_batch(self, batch_id: str, items: List[Dict[str, Any]]):
        raise NotImplementedError('TASK 1: implement enqueue_batch.')

    def process_batch(self, task: Dict[str, Any]) -> bool:
        raise NotImplementedError('TASK 2: implement process_batch.')

    def run_worker_cycle(self) -> Dict[str, int]:
        raise NotImplementedError('TASK 3: implement run_worker_cycle.')
if __name__ == '__main__':
    p = DistributedBatchPipeline(2)
    p.enqueue_batch('b1', [{'id': '1'}])
    print(p.run_worker_cycle())

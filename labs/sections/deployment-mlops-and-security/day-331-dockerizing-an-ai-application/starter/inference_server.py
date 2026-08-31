"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

from typing import Dict, Any, List, Optional

class PagedKVCacheManager:

    def __init__(self, total_blocks: int=16, block_size_tokens: int=4):
        self.block_size = int(block_size_tokens)
        self.total_blocks = int(total_blocks)
        self.free_blocks: List[int] = list(range(total_blocks))
        self.block_tables: Dict[str, List[int]] = {}

    def allocate_for_request(self, req_id: str, num_tokens: int) -> bool:
        raise NotImplementedError('TASK 1: implement allocate_for_request.')

    def append_token(self, req_id: str, current_token_count: int) -> bool:
        raise NotImplementedError('TASK 2: implement append_token.')

    def free_request(self, req_id: str):
        raise NotImplementedError('TASK 3: implement free_request.')

class ContinuousBatchScheduler:

    def __init__(self, cache_manager: PagedKVCacheManager):
        self.cache = cache_manager
        self.waiting_queue: List[Dict[str, Any]] = []
        self.running_batch: List[Dict[str, Any]] = []

    def add_request(self, req_id: str, prompt_tokens: int, max_tokens: int):
        raise NotImplementedError('TASK 4: implement add_request.')

    def step(self) -> List[str]:
        raise NotImplementedError('TASK 5: implement step.')
if __name__ == '__main__':
    c = PagedKVCacheManager(8, 4)
    s = ContinuousBatchScheduler(c)
    s.add_request('r1', 4, 2)
    print('Step 1:', s.step())
    print('Step 2:', s.step())

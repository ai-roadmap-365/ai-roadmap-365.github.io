# Starter: PagedAttention Block Allocator and Scheduler
from typing import Dict, List, Any

class PagedBlockAllocator:
    def __init__(self, num_blocks: int = 64, block_size: int = 16):
        self.num_blocks = num_blocks
        self.block_size = block_size
        self.free_blocks = list(range(num_blocks))
        self.allocated_blocks = set()

    def allocate_block(self) -> int:
        if not self.free_blocks:
            raise MemoryError("OOM")
        blk = self.free_blocks.pop(0)
        self.allocated_blocks.add(blk)
        return blk

    def free_block(self, block_id: int) -> None:
        if block_id in self.allocated_blocks:
            self.allocated_blocks.remove(block_id)
            self.free_blocks.append(block_id)

class RequestState:
    def __init__(self, request_id: str, prompt_len: int, target_gen_len: int):
        self.request_id = request_id
        self.prompt_len = prompt_len
        self.target_gen_len = target_gen_len
        self.generated_tokens = 0
        self.block_table = []
        self.completed = False

    @property
    def total_tokens(self) -> int:
        return self.prompt_len + self.generated_tokens

class ContinuousBatchScheduler:
    def __init__(self, allocator: PagedBlockAllocator, max_batch_size: int = 8):
        self.allocator = allocator
        self.max_batch_size = max_batch_size
        self.waiting_queue = []
        self.running_batch = []
        self.completed_requests = []

    def add_request(self, req: RequestState) -> None:
        self.waiting_queue.append(req)

    def step_iteration(self) -> Dict[str, Any]:
        return {"active_requests": 0, "tokens_emitted": 0}

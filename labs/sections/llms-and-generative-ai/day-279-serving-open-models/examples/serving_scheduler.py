# PagedAttention Block Allocator and Continuous Batching Scheduler Simulator
import math
from typing import Dict, List, Any, Optional, Set

class PagedBlockAllocator:
    """Manages a pool of fixed-size physical memory blocks in simulated GPU VRAM."""

    def __init__(self, num_blocks: int = 64, block_size: int = 16):
        self.num_blocks = num_blocks
        self.block_size = block_size
        self.free_blocks: List[int] = list(range(num_blocks))
        self.allocated_blocks: Set[int] = set()

    def allocate_block(self) -> int:
        """Allocates a single physical block from the free list."""
        if not self.free_blocks:
            raise MemoryError("GPU VRAM Out of Memory: No free PagedAttention blocks available.")
        block_id = self.free_blocks.pop(0)
        self.allocated_blocks.add(block_id)
        return block_id

    def free_block(self, block_id: int) -> None:
        """Returns a physical block to the free list."""
        if block_id in self.allocated_blocks:
            self.allocated_blocks.remove(block_id)
            self.free_blocks.append(block_id)

class RequestState:
    """Tracks the execution and logical block table of a single generation request."""

    def __init__(self, request_id: str, prompt_len: int, target_gen_len: int):
        self.request_id = request_id
        self.prompt_len = prompt_len
        self.target_gen_len = target_gen_len
        self.generated_tokens = 0
        self.block_table: List[int] = []
        self.completed = False

    @property
    def total_tokens(self) -> int:
        return self.prompt_len + self.generated_tokens

class ContinuousBatchScheduler:
    """Simulates iteration-level continuous batching with PagedAttention."""

    def __init__(self, allocator: PagedBlockAllocator, max_batch_size: int = 8):
        self.allocator = allocator
        self.max_batch_size = max_batch_size
        self.waiting_queue: List[RequestState] = []
        self.running_batch: List[RequestState] = []
        self.completed_requests: List[RequestState] = []

    def add_request(self, req: RequestState) -> None:
        self.waiting_queue.append(req)

    def step_iteration(self) -> Dict[str, Any]:
        """Executes a single token generation step across all active requests."""
        # 1. Admit new requests from waiting queue if capacity allows
        while len(self.running_batch) < self.max_batch_size and self.waiting_queue:
            candidate = self.waiting_queue.pop(0)
            # Allocate initial blocks for prompt
            needed_blocks = math.ceil(candidate.prompt_len / self.allocator.block_size)
            try:
                for _ in range(needed_blocks):
                    candidate.block_table.append(self.allocator.allocate_block())
                self.running_batch.append(candidate)
            except MemoryError:
                # Put back in queue if memory exhausted
                self.waiting_queue.insert(0, candidate)
                break

        tokens_generated_this_step = 0

        # 2. Generate one token for every running request
        still_running = []
        for req in self.running_batch:
            req.generated_tokens += 1
            tokens_generated_this_step += 1

            # Check if additional block allocation is needed
            current_capacity = len(req.block_table) * self.allocator.block_size
            if req.total_tokens > current_capacity:
                req.block_table.append(self.allocator.allocate_block())

            # Check completion
            if req.generated_tokens >= req.target_gen_len:
                req.completed = True
                # Free physical blocks immediately (Continuous Batching)
                for blk in req.block_table:
                    self.allocator.free_block(blk)
                self.completed_requests.append(req)
            else:
                still_running.append(req)

        self.running_batch = still_running

        return {
            "active_requests": len(self.running_batch),
            "waiting_requests": len(self.waiting_queue),
            "completed_requests": len(self.completed_requests),
            "allocated_blocks": len(self.allocator.allocated_blocks),
            "tokens_emitted": tokens_generated_this_step
        }

    def compute_fragmentation_metrics(self, max_context_window: int = 128) -> Dict[str, float]:
        """Compares PagedAttention memory efficiency against Static Batching."""
        total_paged_blocks = len(self.allocator.allocated_blocks)
        paged_vram_tokens = total_paged_blocks * self.allocator.block_size

        # In static batching, every active + waiting request reserves max_context_window
        total_reqs = len(self.running_batch) + len(self.waiting_queue)
        static_vram_tokens = total_reqs * max_context_window

        actual_used_tokens = sum(r.total_tokens for r in self.running_batch)
        paged_waste = (1.0 - (actual_used_tokens / paged_vram_tokens)) * 100.0 if paged_vram_tokens > 0 else 0.0
        static_waste = (1.0 - (actual_used_tokens / static_vram_tokens)) * 100.0 if static_vram_tokens > 0 else 0.0

        return {
            "paged_used_blocks": float(total_paged_blocks),
            "paged_waste_percentage": max(0.0, float(paged_waste)),
            "static_waste_percentage": max(0.0, float(static_waste))
        }

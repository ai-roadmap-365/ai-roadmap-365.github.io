from typing import Dict, Any, List, Optional

class PagedKVCacheManager:
    def __init__(self, total_blocks: int = 16, block_size_tokens: int = 4):
        self.block_size = int(block_size_tokens)
        self.total_blocks = int(total_blocks)
        self.free_blocks: List[int] = list(range(total_blocks))
        self.block_tables: Dict[str, List[int]] = {}
        
    def allocate_for_request(self, req_id: str, num_tokens: int) -> bool:
        needed_blocks = (num_tokens + self.block_size - 1) // self.block_size
        if len(self.free_blocks) < needed_blocks:
            return False
            
        allocated = []
        for _ in range(needed_blocks):
            allocated.append(self.free_blocks.pop(0))
        self.block_tables[req_id] = allocated
        return True

    def append_token(self, req_id: str, current_token_count: int) -> bool:
        if current_token_count % self.block_size == 0:
            if not self.free_blocks:
                return False
            new_block = self.free_blocks.pop(0)
            self.block_tables[req_id].append(new_block)
        return True

    def free_request(self, req_id: str):
        if req_id in self.block_tables:
            for b in self.block_tables[req_id]:
                self.free_blocks.append(b)
            del self.block_tables[req_id]

class ContinuousBatchScheduler:
    def __init__(self, cache_manager: PagedKVCacheManager):
        self.cache = cache_manager
        self.waiting_queue: List[Dict[str, Any]] = []
        self.running_batch: List[Dict[str, Any]] = []
        
    def add_request(self, req_id: str, prompt_tokens: int, max_tokens: int):
        self.waiting_queue.append({
            "req_id": req_id,
            "prompt_tokens": prompt_tokens,
            "max_tokens": max_tokens,
            "generated_tokens": 0
        })

    def step(self) -> List[str]:
        admitted = []
        for req in list(self.waiting_queue):
            if self.cache.allocate_for_request(req["req_id"], req["prompt_tokens"]):
                self.running_batch.append(req)
                self.waiting_queue.remove(req)
                admitted.append(req["req_id"])
            else:
                break
                
        completed = []
        for req in list(self.running_batch):
            req["generated_tokens"] += 1
            current_total = req["prompt_tokens"] + req["generated_tokens"]
            self.cache.append_token(req["req_id"], current_total)
            
            if req["generated_tokens"] >= req["max_tokens"]:
                self.cache.free_request(req["req_id"])
                self.running_batch.remove(req)
                completed.append(req["req_id"])
                
        return completed

if __name__ == "__main__":
    c = PagedKVCacheManager(8, 4)
    s = ContinuousBatchScheduler(c)
    s.add_request("r1", 4, 2)
    print("Step 1:", s.step())
    print("Step 2:", s.step())

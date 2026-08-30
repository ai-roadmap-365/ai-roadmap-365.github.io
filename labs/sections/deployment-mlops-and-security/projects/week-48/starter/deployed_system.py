from typing import Dict, Any, List, Optional
import math
import time

class PagedCache:
    def __init__(self, total_blocks: int = 16, block_size: int = 4):
        self.block_size = block_size
        self.free_blocks = list(range(total_blocks))
        self.tables: Dict[str, List[int]] = {}
        
    def allocate(self, req_id: str, tokens: int) -> bool:
        needed = (tokens + self.block_size - 1) // self.block_size
        if len(self.free_blocks) < needed:
            return False
        self.tables[req_id] = [self.free_blocks.pop(0) for _ in range(needed)]
        return True

    def free(self, req_id: str):
        if req_id in self.tables:
            for b in self.tables[req_id]:
                self.free_blocks.append(b)
            del self.tables[req_id]

class ServingWorker:
    def __init__(self, worker_id: str, total_blocks: int = 16):
        self.worker_id = worker_id
        self.cache = PagedCache(total_blocks=total_blocks)
        self.active_batch: List[Dict[str, Any]] = []
        self.is_healthy = True
        
    def add_request(self, req_id: str, prompt_tokens: int, max_tokens: int) -> bool:
        if not self.cache.allocate(req_id, prompt_tokens):
            return False
        self.active_batch.append({
            "req_id": req_id,
            "max_tokens": max_tokens,
            "generated": 0
        })
        return True

    def step(self) -> List[str]:
        completed = []
        for req in list(self.active_batch):
            req["generated"] += 1
            if req["generated"] >= req["max_tokens"]:
                self.cache.free(req["req_id"])
                self.active_batch.remove(req)
                completed.append(req["req_id"])
        return completed

class DeployedAISystem:
    def __init__(self, num_workers: int = 2, failure_threshold: int = 3):
        self.workers = [ServingWorker(f"worker_{i}") for i in range(num_workers)]
        self.failure_threshold = failure_threshold
        self.circuit_state = "CLOSED"
        self.total_routed = 0
        
    def route_request(self, req_id: str, prompt_tokens: int, max_tokens: int) -> Dict[str, Any]:
        if self.circuit_state == "OPEN":
            return {"status": "CIRCUIT_FALLBACK", "response": "Service degraded; fallback emitted."}
            
        healthy = [w for w in self.workers if w.is_healthy]
        if not healthy:
            self.circuit_state = "OPEN"
            return {"status": "CIRCUIT_FALLBACK", "response": "No healthy workers."}
            
        # Select least busy worker
        chosen = min(healthy, key=lambda w: len(w.active_batch))
        success = chosen.add_request(req_id, prompt_tokens, max_tokens)
        
        if success:
            self.total_routed += 1
            return {
                "status": "ACCEPTED",
                "worker_id": chosen.worker_id,
                "worker_active_count": len(chosen.active_batch)
            }
        else:
            return {"status": "VRAM_THROTTLED", "worker_id": chosen.worker_id}

    def step_all(self) -> Dict[str, List[str]]:
        results = {}
        for w in self.workers:
            if w.is_healthy:
                results[w.worker_id] = w.step()
        return results

if __name__ == "__main__":
    sys = DeployedAISystem(num_workers=2)
    print("Route 1:", sys.route_request("r1", 4, 2))
    print("Route 2:", sys.route_request("r2", 4, 3))
    print("Step:", sys.step_all())

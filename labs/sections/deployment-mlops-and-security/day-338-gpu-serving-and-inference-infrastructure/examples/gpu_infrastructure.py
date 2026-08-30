import time
from typing import Dict, Any, List, Optional

class GPUServingInfrastructureSimulator:
    def __init__(self, max_batch_size: int = 4, max_queue_delay_ms: float = 5.0):
        self.max_batch = int(max_batch_size)
        self.max_delay_ms = float(max_queue_delay_ms)
        self.vram_pool_mb = 16384
        self.allocated_models: Dict[str, int] = {}
        self.incoming_queue: List[Dict[str, Any]] = []
        self.execution_log: List[Dict[str, Any]] = []

    def load_model_to_vram(self, model_name: str, required_vram_mb: int) -> bool:
        used_vram = sum(self.allocated_models.values())
        if (used_vram + required_vram_mb) > self.vram_pool_mb:
            return False
        self.allocated_models[model_name] = required_vram_mb
        return True

    def enqueue_request(self, req_id: str, prompt: str, arrival_time: float):
        self.incoming_queue.append({
            "req_id": req_id,
            "prompt": prompt,
            "arrival_time": arrival_time
        })

    def process_dynamic_batch(self, current_time: float) -> Optional[Dict[str, Any]]:
        if not self.incoming_queue:
            return None

        oldest_arrival = self.incoming_queue[0]["arrival_time"]
        delay_elapsed_ms = (current_time - oldest_arrival) * 1000.0

        if len(self.incoming_queue) >= self.max_batch or delay_elapsed_ms >= self.max_delay_ms:
            batch_size = min(len(self.incoming_queue), self.max_batch)
            batch = [self.incoming_queue.pop(0) for _ in range(batch_size)]
            
            event = {
                "batch_size": len(batch),
                "request_ids": [b["req_id"] for b in batch],
                "avg_queue_delay_ms": round(sum((current_time - b["arrival_time"]) * 1000.0 for b in batch) / len(batch), 2),
                "timestamp": current_time
            }
            self.execution_log.append(event)
            return event

        return None

if __name__ == "__main__":
    s = GPUServingInfrastructureSimulator(2, 5.0)
    s.enqueue_request("r1", "p1", 100.0)
    s.enqueue_request("r2", "p2", 100.001)
    print(s.process_dynamic_batch(100.002))

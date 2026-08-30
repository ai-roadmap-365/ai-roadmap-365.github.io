import time
from typing import Dict, Any, List, Optional

class ReplicaWorker:
    def __init__(self, replica_id: str):
        self.replica_id = replica_id
        self.active_requests = 0
        self.is_healthy = True
        self.consecutive_failures = 0

class ProductionAIGateway:
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 5.0):
        self.failure_threshold = int(failure_threshold)
        self.cooldown_sec = float(cooldown_seconds)
        self.replicas: Dict[str, ReplicaWorker] = {}
        self.circuit_state = "CLOSED"
        self.last_state_change = time.time()
        self.telemetry_metrics = {
            "total_routed": 0,
            "circuit_fallbacks": 0,
            "lor_selections": []
        }

    def register_replica(self, replica_id: str):
        self.replicas[replica_id] = ReplicaWorker(replica_id)

    def select_replica_lor(self) -> Optional[ReplicaWorker]:
        healthy = [r for r in self.replicas.values() if r.is_healthy]
        if not healthy:
            return None
        return min(healthy, key=lambda r: r.active_requests)

    def route_request(self, prompt: str, current_time: float) -> Dict[str, Any]:
        if self.circuit_state == "OPEN":
            if (current_time - self.last_state_change) >= self.cooldown_sec:
                self.circuit_state = "HALF_OPEN"
                self.last_state_change = current_time
            else:
                self.telemetry_metrics["circuit_fallbacks"] += 1
                return {"status": "FALLBACK", "response": "Cached graceful fallback response."}

        worker = self.select_replica_lor()
        if not worker:
            self.circuit_state = "OPEN"
            self.last_state_change = current_time
            self.telemetry_metrics["circuit_fallbacks"] += 1
            return {"status": "FALLBACK", "response": "All replicas unhealthy; returning fallback."}

        worker.active_requests += 1
        self.telemetry_metrics["total_routed"] += 1
        self.telemetry_metrics["lor_selections"].append(worker.replica_id)

        return {
            "status": "ROUTED",
            "assigned_replica": worker.replica_id,
            "active_on_replica": worker.active_requests,
            "circuit_state": self.circuit_state
        }

    def complete_request(self, replica_id: str, success: bool, current_time: float):
        worker = self.replicas.get(replica_id)
        if not worker:
            return
        worker.active_requests = max(0, worker.active_requests - 1)

        if success:
            worker.consecutive_failures = 0
            if self.circuit_state == "HALF_OPEN":
                self.circuit_state = "CLOSED"
                self.last_state_change = current_time
        else:
            worker.consecutive_failures += 1
            if worker.consecutive_failures >= self.failure_threshold:
                worker.is_healthy = False
                if all(not r.is_healthy for r in self.replicas.values()):
                    self.circuit_state = "OPEN"
                    self.last_state_change = current_time

if __name__ == "__main__":
    g = ProductionAIGateway(2, 5.0)
    g.register_replica("w1")
    print(g.route_request("hi", 100.0))

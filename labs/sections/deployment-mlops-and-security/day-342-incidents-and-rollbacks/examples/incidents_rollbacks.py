import time
from typing import Dict, Any, List, Optional

class AIIncidentRollbackEngine:
    def __init__(self, error_threshold_pct: float = 2.0, min_requests_to_evaluate: int = 10):
        self.error_threshold = float(error_threshold_pct)
        self.min_requests = int(min_requests_to_evaluate)
        self.active_variant = "CANDIDATE_V2"
        self.baseline_variant = "BASELINE_V1"
        self.circuit_tripped = False
        self.total_candidate_requests = 0
        self.total_candidate_errors = 0
        self.incident_log: List[Dict[str, Any]] = []

    def record_request_outcome(self, is_error: bool):
        if not self.circuit_tripped:
            self.total_candidate_requests += 1
            if is_error:
                self.total_candidate_errors += 1
            self._evaluate_circuit_breaker()

    def _evaluate_circuit_breaker(self):
        if self.total_candidate_requests >= self.min_requests:
            error_rate = (self.total_candidate_errors / self.total_candidate_requests) * 100.0
            if error_rate > self.error_threshold:
                self.circuit_tripped = True
                self.active_variant = self.baseline_variant
                
                event = {
                    "incident_id": f"INC-{int(time.time())}",
                    "severity": "P1",
                    "action": "CIRCUIT_BREAKER_ROLLBACK",
                    "triggered_error_rate_pct": round(error_rate, 2),
                    "reverted_to": self.baseline_variant,
                    "timestamp": time.time()
                }
                self.incident_log.append(event)

    def route_inference(self, prompt: str) -> str:
        return f"[{self.active_variant}] Processed: {prompt}"

if __name__ == "__main__":
    e = AIIncidentRollbackEngine()
    print(e.route_inference("test"))

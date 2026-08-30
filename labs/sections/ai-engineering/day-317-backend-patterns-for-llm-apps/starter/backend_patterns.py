import time
import json
from typing import Dict, Any, List, Optional, Tuple

class ResilientLLMBackend:
    def __init__(self, failure_threshold: int = 3, reset_timeout_seconds: float = 1.0):
        self.failure_threshold = int(failure_threshold)
        self.reset_timeout = float(reset_timeout_seconds)
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.failure_count = 0
        self.last_state_change = time.time()
        self.idempotency_store: Dict[str, Dict[str, Any]] = {}
        
    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.last_state_change = time.time()
            
    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
        
    def check_circuit_state(self) -> str:
        if self.state == "OPEN":
            if time.time() - self.last_state_change >= self.reset_timeout:
                self.state = "HALF-OPEN"
        return self.state

    def process_request(self, idempotency_key: str, prompt: str, simulate_upstream_fail: bool = False) -> Dict[str, Any]:
        if idempotency_key in self.idempotency_store:
            return {
                "status": "REPLAYED",
                "idempotency_key": idempotency_key,
                "cached": True,
                "response": self.idempotency_store[idempotency_key]["response"]
            }
            
        current_state = self.check_circuit_state()
        if current_state == "OPEN":
            fallback_response = f"[FALLBACK_BACKUP_MODEL] Processed: {prompt}"
            self.idempotency_store[idempotency_key] = {"response": fallback_response}
            return {
                "status": "CIRCUIT_OPEN_FALLBACK",
                "provider": "backup_replica",
                "response": fallback_response,
                "cached": False
            }
            
        if simulate_upstream_fail:
            self.record_failure()
            return {"status": "UPSTREAM_ERROR", "error": "503 Service Unavailable"}
            
        self.record_success()
        primary_response = f"[PRIMARY_CLAUDE] Processed: {prompt}"
        self.idempotency_store[idempotency_key] = {"response": primary_response}
        
        return {
            "status": "SUCCESS",
            "provider": "primary_model",
            "response": primary_response,
            "cached": False
        }

if __name__ == "__main__":
    backend = ResilientLLMBackend()
    print("Normal:", backend.process_request("k1", "Hello"))

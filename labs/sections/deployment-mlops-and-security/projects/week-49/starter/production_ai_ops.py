import re
import uuid
import time
import hashlib
import numpy as np
from typing import Dict, Any, List, Optional

class ProductionAIOpsPlatform:
    def __init__(self, canary_pct: int = 20, error_threshold_pct: float = 5.0, min_eval_requests: int = 10):
        self.canary_pct = canary_pct
        self.error_threshold = error_threshold_pct
        self.min_eval = min_eval_requests
        
        self.circuit_tripped = False
        self.baseline_variant = "BASELINE_V1"
        self.candidate_variant = "CANDIDATE_V2"
        
        self.latencies_ms: List[float] = []
        self.total_requests = 0
        self.total_errors = 0
        self.tenant_ledger: Dict[str, float] = {}
        self.emitted_logs: List[Dict[str, Any]] = []

    def sanitize_pii(self, text: str) -> str:
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]', text)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]', text)
        text = re.sub(r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[REDACTED_CC]', text)
        return text

    def _get_variant(self, user_id: str) -> str:
        if self.circuit_tripped:
            return self.baseline_variant
        h = int(hashlib.md5(f"flag:{user_id}".encode("utf-8")).hexdigest()[:8], 16) % 100
        return self.candidate_variant if h < self.canary_pct else self.baseline_variant

    def execute_inference(self, tenant_id: str, user_id: str, prompt: str, 
                          prompt_tokens: int = 100, completion_tokens: int = 50, 
                          simulate_error: bool = False, latency_ms: float = 120.0) -> Dict[str, Any]:
        trace_id = uuid.uuid4().hex
        clean_prompt = self.sanitize_pii(prompt)
        variant = self._get_variant(user_id)
        
        self.total_requests += 1
        if simulate_error:
            self.total_errors += 1
        else:
            self.latencies_ms.append(float(latency_ms))

        if not self.circuit_tripped and self.total_requests >= self.min_eval:
            err_rate = (self.total_errors / self.total_requests) * 100.0
            if err_rate > self.error_threshold:
                self.circuit_tripped = True

        cost = (prompt_tokens * 0.000002) + (completion_tokens * 0.000006)
        self.tenant_ledger[tenant_id] = round(self.tenant_ledger.get(tenant_id, 0.0) + cost, 6)

        log_rec = {
            "trace_id": trace_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "variant": variant,
            "prompt_sanitized": clean_prompt,
            "tokens": prompt_tokens + completion_tokens,
            "cost_usd": round(cost, 6),
            "is_error": simulate_error,
            "circuit_tripped": self.circuit_tripped,
            "timestamp": time.time()
        }
        self.emitted_logs.append(log_rec)
        return log_rec

    def get_platform_telemetry(self) -> Dict[str, Any]:
        p50 = float(np.percentile(self.latencies_ms, 50)) if self.latencies_ms else 0.0
        p95 = float(np.percentile(self.latencies_ms, 95)) if self.latencies_ms else 0.0
        p99 = float(np.percentile(self.latencies_ms, 99)) if self.latencies_ms else 0.0
        err_rate = (self.total_errors / self.total_requests * 100.0) if self.total_requests > 0 else 0.0
        
        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate_pct": round(err_rate, 2),
            "p50_latency_ms": round(p50, 2),
            "p95_latency_ms": round(p95, 2),
            "p99_latency_ms": round(p99, 2),
            "circuit_tripped": self.circuit_tripped,
            "total_tenants": len(self.tenant_ledger),
            "total_spend_usd": round(sum(self.tenant_ledger.values()), 4)
        }

if __name__ == "__main__":
    ops = ProductionAIOpsPlatform()
    print(ops.execute_inference("t1", "u1", "test query"))

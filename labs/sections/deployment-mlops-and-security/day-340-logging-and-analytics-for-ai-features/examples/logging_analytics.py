import re
import json
import uuid
import time
from typing import Dict, Any, List, Optional

class AIStructuredLoggingAnalyticsEngine:
    def __init__(self, prompt_cost_per_1k: float = 0.002, completion_cost_per_1k: float = 0.006):
        self.prompt_rate = prompt_cost_per_1k / 1000.0
        self.completion_rate = completion_cost_per_1k / 1000.0
        self.tenant_ledger: Dict[str, Dict[str, Any]] = {}
        self.emitted_logs: List[Dict[str, Any]] = []

    def sanitize_pii(self, text: str) -> str:
        sanitized = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]', text)
        sanitized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]', sanitized)
        sanitized = re.sub(r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[REDACTED_CC]', sanitized)
        return sanitized

    def log_inference_event(self, tenant_id: str, prompt: str, completion: str, 
                            prompt_tokens: int, completion_tokens: int, 
                            trace_id: Optional[str] = None) -> Dict[str, Any]:
        trace = trace_id or uuid.uuid4().hex
        clean_prompt = self.sanitize_pii(prompt)
        clean_completion = self.sanitize_pii(completion)

        cost = (prompt_tokens * self.prompt_rate) + (completion_tokens * self.completion_rate)

        log_record = {
            "trace_id": trace,
            "tenant_id": tenant_id,
            "prompt_sanitized": clean_prompt,
            "completion_sanitized": clean_completion,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost_usd": round(cost, 6),
            "timestamp": time.time()
        }
        self.emitted_logs.append(log_record)

        if tenant_id not in self.tenant_ledger:
            self.tenant_ledger[tenant_id] = {
                "total_requests": 0,
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "total_cost_usd": 0.0
            }
        
        self.tenant_ledger[tenant_id]["total_requests"] += 1
        self.tenant_ledger[tenant_id]["total_prompt_tokens"] += prompt_tokens
        self.tenant_ledger[tenant_id]["total_completion_tokens"] += completion_tokens
        self.tenant_ledger[tenant_id]["total_cost_usd"] = round(
            self.tenant_ledger[tenant_id]["total_cost_usd"] + cost, 6
        )

        return log_record

if __name__ == "__main__":
    e = AIStructuredLoggingAnalyticsEngine()
    print(e.log_inference_event("t1", "Email is test@example.com", "OK", 100, 50))

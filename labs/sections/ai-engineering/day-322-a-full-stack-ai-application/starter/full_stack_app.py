import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple

class FullStackAIAppEngine:
    def __init__(self):
        self.tenants: Dict[str, Dict[str, Any]] = {
            "tenant_alpha": {
                "key_hash": hashlib.sha256(b"sk_alpha_123").hexdigest(),
                "balance": 10.0,
                "reserved_holds": 0.0,
                "rpm_limit": 60,
                "requests_this_min": 0,
                "last_reset": time.time()
            },
            "tenant_poor": {
                "key_hash": hashlib.sha256(b"sk_poor_123").hexdigest(),
                "balance": 0.01,
                "reserved_holds": 0.0,
                "rpm_limit": 10,
                "requests_this_min": 0,
                "last_reset": time.time()
            }
        }
        self.cache: Dict[str, str] = {}
        self.active_holds: Dict[str, Dict[str, Any]] = {}
        self.providers = ["primary_claude", "secondary_openai", "backup_vllm"]
        
    def process_chat_request(
        self,
        tenant_id: str,
        raw_key: str,
        prompt: str,
        simulated_failing_providers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        if tenant_id not in self.tenants:
            return {"status": "AUTH_ERROR", "message": "Invalid tenant ID"}
            
        tenant = self.tenants[tenant_id]
        if hashlib.sha256(raw_key.encode()).hexdigest() != tenant["key_hash"]:
            return {"status": "AUTH_ERROR", "message": "Invalid API key"}
            
        now = time.time()
        if now - tenant["last_reset"] > 60:
            tenant["requests_this_min"] = 0
            tenant["last_reset"] = now
            
        if tenant["requests_this_min"] >= tenant["rpm_limit"]:
            return {"status": "RATE_LIMITED", "message": "RPM limit exceeded"}
            
        cache_key = f"{tenant_id}:{prompt.strip().lower()}"
        if cache_key in self.cache:
            return {
                "status": "SUCCESS",
                "cached": True,
                "cost_usd": 0.0,
                "response": self.cache[cache_key],
                "remaining_balance": round(tenant["balance"], 6)
            }
            
        est_cost = 0.030
        available_balance = tenant["balance"] - tenant["reserved_holds"]
        if available_balance < est_cost:
            return {"status": "PAYMENT_REQUIRED", "message": "Insufficient credit balance"}
            
        hold_id = f"hold_{len(self.active_holds)+1}"
        tenant["reserved_holds"] += est_cost
        tenant["requests_this_min"] += 1
        
        failing = set(simulated_failing_providers or [])
        resolved_provider = None
        attempted_providers = []
        
        for p in self.providers:
            attempted_providers.append(p)
            if p not in failing:
                resolved_provider = p
                break
                
        if not resolved_provider:
            tenant["reserved_holds"] -= est_cost
            return {"status": "UPSTREAM_OUTAGE", "attempted": attempted_providers}
            
        actual_cost = 0.00465
        tenant["reserved_holds"] -= est_cost
        tenant["balance"] -= actual_cost
        
        full_response = f"[{resolved_provider}] Response for: {prompt}"
        self.cache[cache_key] = full_response
        
        return {
            "status": "SUCCESS",
            "cached": False,
            "resolved_provider": resolved_provider,
            "fallback_occurred": len(attempted_providers) > 1,
            "actual_cost_usd": actual_cost,
            "remaining_balance": round(tenant["balance"], 6),
            "response": full_response
        }

if __name__ == "__main__":
    app = FullStackAIAppEngine()
    print("Normal:", app.process_chat_request("tenant_alpha", "sk_alpha_123", "Hi"))

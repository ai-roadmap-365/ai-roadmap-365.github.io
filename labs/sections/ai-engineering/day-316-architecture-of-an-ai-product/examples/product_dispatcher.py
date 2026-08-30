import time
import json
from typing import Dict, Any, Tuple, List, Optional

class AIProductDispatcher:
    def __init__(self):
        self.tenants: Dict[str, Dict[str, Any]] = {
            "org_alpha": {"credits": 50.0, "rate_limit_per_min": 60, "requests_this_min": 0, "last_reset": time.time()},
            "org_beta": {"credits": 0.0, "rate_limit_per_min": 10, "requests_this_min": 0, "last_reset": time.time()},
            "org_gamma": {"credits": 10.0, "rate_limit_per_min": 2, "requests_this_min": 0, "last_reset": time.time()}
        }
        self.cache: Dict[str, str] = {}
        
    def authenticate_and_gate(self, tenant_id: str) -> Tuple[bool, str]:
        if tenant_id not in self.tenants:
            return False, "Unauthorized: Invalid Tenant ID"
            
        tenant = self.tenants[tenant_id]
        now = time.time()
        
        if now - tenant["last_reset"] > 60:
            tenant["requests_this_min"] = 0
            tenant["last_reset"] = now
            
        if tenant["requests_this_min"] >= tenant["rate_limit_per_min"]:
            return False, "Too Many Requests: Rate limit exceeded"
            
        if tenant["credits"] <= 0.0:
            return False, "Payment Required: Zero credit balance"
            
        tenant["requests_this_min"] += 1
        return True, "OK"

    def dispatch_chat(self, tenant_id: str, prompt: str) -> Dict[str, Any]:
        auth_ok, msg = self.authenticate_and_gate(tenant_id)
        if not auth_ok:
            return {"status": "ERROR", "error_code": msg, "tokens_streamed": []}
            
        cache_key = f"{tenant_id}:{prompt.strip().lower()}"
        if cache_key in self.cache:
            return {
                "status": "CACHED",
                "response": self.cache[cache_key],
                "cost_usd": 0.0,
                "cached": True,
                "remaining_credits": round(self.tenants[tenant_id]["credits"], 4)
            }
            
        mock_tokens = ["This", " is", " a", " streamed", " AI", " response."]
        full_response = "".join(mock_tokens)
        
        self.tenants[tenant_id]["credits"] -= 0.002
        self.cache[cache_key] = full_response
        
        return {
            "status": "SUCCESS",
            "tokens_streamed": mock_tokens,
            "response": full_response,
            "cost_usd": 0.002,
            "cached": False,
            "remaining_credits": round(self.tenants[tenant_id]["credits"], 4)
        }

if __name__ == "__main__":
    dispatcher = AIProductDispatcher()
    print("Org Alpha:", dispatcher.dispatch_chat("org_alpha", "Hello"))

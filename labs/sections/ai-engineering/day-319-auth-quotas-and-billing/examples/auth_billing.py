import hashlib
import time
from typing import Dict, Any, Optional, Tuple

class AuthBillingEngine:
    def __init__(self):
        self.tenants: Dict[str, Dict[str, Any]] = {}
        self.active_holds: Dict[str, Dict[str, Any]] = {}
        
    def register_tenant(self, tenant_id: str, raw_api_key: str, initial_credits: float = 10.0, rpm_limit: int = 60, tpm_limit: int = 100000):
        key_hash = hashlib.sha256(raw_api_key.encode()).hexdigest()
        self.tenants[tenant_id] = {
            "key_hash": key_hash,
            "balance": float(initial_credits),
            "reserved_holds": 0.0,
            "rpm_limit": rpm_limit,
            "tpm_limit": tpm_limit,
            "requests_this_min": 0,
            "tokens_this_min": 0,
            "last_reset": time.time()
        }
        
    def authenticate_and_reserve_hold(self, tenant_id: str, raw_api_key: str, estimated_cost: float = 0.02, est_tokens: int = 500) -> Tuple[bool, str, Optional[str]]:
        if tenant_id not in self.tenants:
            return False, "Unauthorized: Unknown Tenant", None
            
        tenant = self.tenants[tenant_id]
        if hashlib.sha256(raw_api_key.encode()).hexdigest() != tenant["key_hash"]:
            return False, "Unauthorized: Invalid API Key", None
            
        now = time.time()
        if now - tenant["last_reset"] > 60:
            tenant["requests_this_min"] = 0
            tenant["tokens_this_min"] = 0
            tenant["last_reset"] = now
            
        if tenant["requests_this_min"] >= tenant["rpm_limit"]:
            return False, "Rate Limit Exceeded: RPM limit reached", None
            
        if tenant["tokens_this_min"] + est_tokens > tenant["tpm_limit"]:
            return False, "Rate Limit Exceeded: TPM limit reached", None
            
        available_balance = tenant["balance"] - tenant["reserved_holds"]
        if available_balance < estimated_cost:
            return False, "Payment Required: Insufficient available credit", None
            
        hold_id = f"hold_{len(self.active_holds)+1}"
        tenant["reserved_holds"] += estimated_cost
        tenant["requests_this_min"] += 1
        tenant["tokens_this_min"] += est_tokens
        
        self.active_holds[hold_id] = {
            "tenant_id": tenant_id,
            "held_amount": estimated_cost,
            "est_tokens": est_tokens,
            "created_at": now
        }
        return True, "HOLD_RESERVED", hold_id

    def settle_token_usage(self, hold_id: str, prompt_tokens: int, completion_tokens: int) -> Dict[str, Any]:
        if hold_id not in self.active_holds:
            return {"status": "ERROR", "message": "Invalid hold ID"}
            
        hold = self.active_holds.pop(hold_id)
        tenant = self.tenants[hold["tenant_id"]]
        
        actual_cost = (prompt_tokens * 3.0 / 1_000_000) + (completion_tokens * 15.0 / 1_000_000)
        actual_cost = round(actual_cost, 6)
        
        tenant["reserved_holds"] -= hold["held_amount"]
        tenant["balance"] -= actual_cost
        
        return {
            "status": "SETTLED",
            "hold_id": hold_id,
            "actual_cost_usd": actual_cost,
            "remaining_balance": round(tenant["balance"], 6),
            "available_balance": round(tenant["balance"] - tenant["reserved_holds"], 6)
        }

if __name__ == "__main__":
    engine = AuthBillingEngine()
    engine.register_tenant("org_1", "key123", 5.0)
    print(engine.authenticate_and_reserve_hold("org_1", "key123", 0.02))

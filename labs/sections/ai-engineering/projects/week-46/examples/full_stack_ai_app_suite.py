import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple

class FullStackAIAppSuite:
    def __init__(self):
        self.tenants: Dict[str, Dict[str, Any]] = {}
        self.exact_cache: Dict[str, str] = {}
        self.semantic_cache: List[Dict[str, Any]] = []
        self.active_holds: Dict[str, Dict[str, Any]] = {}
        self.providers = ["primary_claude", "secondary_openai", "backup_vllm"]
        
    def register_tenant(
        self,
        tenant_id: str,
        raw_key: str,
        balance: float = 10.0,
        rpm_limit: int = 60,
        tpm_limit: int = 100000
    ):
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        self.tenants[tenant_id] = {
            "key_hash": key_hash,
            "balance": float(balance),
            "reserved_holds": 0.0,
            "rpm_limit": int(rpm_limit),
            "tpm_limit": int(tpm_limit),
            "requests_this_min": 0,
            "tokens_this_min": 0,
            "last_reset": time.time()
        }
        
    @staticmethod
    def _mock_embedding(text: str) -> List[float]:
        words = text.lower().split()
        return [float(len(text)), float(len(words)), float(sum(ord(c) for c in text[:5]) if text else 0.0)]

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return round(dot / (norm1 * norm2), 4)

    def execute_chat_transaction(
        self,
        tenant_id: str,
        raw_key: str,
        prompt: str,
        simulated_failing_providers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        # 1. Auth & Rate Limit Check
        if tenant_id not in self.tenants:
            return {"status": "AUTH_ERROR", "message": "Unknown tenant ID"}
            
        tenant = self.tenants[tenant_id]
        if hashlib.sha256(raw_key.encode()).hexdigest() != tenant["key_hash"]:
            return {"status": "AUTH_ERROR", "message": "Invalid API key"}
            
        now = time.time()
        if now - tenant["last_reset"] > 60:
            tenant["requests_this_min"] = 0
            tenant["tokens_this_min"] = 0
            tenant["last_reset"] = now
            
        if tenant["requests_this_min"] >= tenant["rpm_limit"]:
            return {"status": "RATE_LIMITED", "message": "RPM limit reached"}
            
        # 2. Multi-Tier Cache Check
        cache_key = f"{tenant_id}:{prompt.strip().lower()}"
        if cache_key in self.exact_cache:
            return {
                "status": "SUCCESS",
                "tier": "TIER_1_EXACT_CACHE",
                "cost_usd": 0.0,
                "response": self.exact_cache[cache_key],
                "remaining_balance": round(tenant["balance"], 6)
            }
            
        q_vec = self._mock_embedding(prompt)
        for entry in self.semantic_cache:
            if entry["tenant_id"] == tenant_id:
                sim = self._cosine_similarity(q_vec, entry["embedding"])
                if sim >= 0.95:
                    return {
                        "status": "SUCCESS",
                        "tier": "TIER_2_SEMANTIC_CACHE",
                        "cost_usd": 0.0,
                        "response": entry["response"],
                        "remaining_balance": round(tenant["balance"], 6)
                    }
                    
        # 3. Two-Phase Pre-Auth Hold
        est_cost = 0.030
        available_balance = tenant["balance"] - tenant["reserved_holds"]
        if available_balance < est_cost:
            return {"status": "PAYMENT_REQUIRED", "message": "Insufficient credit balance"}
            
        hold_id = f"hold_{len(self.active_holds)+1}"
        tenant["reserved_holds"] += est_cost
        tenant["requests_this_min"] += 1
        
        # 4. Vendor Router with Failover
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
            
        # 5. Settlement & Exact Reconciliation
        actual_cost = 0.00512
        tenant["reserved_holds"] -= est_cost
        tenant["balance"] -= actual_cost
        
        response_text = f"[{resolved_provider}] Full-stack response for: {prompt}"
        
        # Store in caches
        self.exact_cache[cache_key] = response_text
        self.semantic_cache.append({
            "tenant_id": tenant_id,
            "embedding": q_vec,
            "response": response_text
        })
        
        return {
            "status": "SUCCESS",
            "tier": "MODEL_GENERATION",
            "resolved_provider": resolved_provider,
            "fallback_occurred": len(attempted_providers) > 1,
            "attempted_providers": attempted_providers,
            "actual_cost_usd": actual_cost,
            "remaining_balance": round(tenant["balance"], 6),
            "response": response_text
        }

if __name__ == "__main__":
    suite = FullStackAIAppSuite()
    suite.register_tenant("org_1", "sk_1", 5.0)
    print(suite.execute_chat_transaction("org_1", "sk_1", "Hello Full-Stack AI"))

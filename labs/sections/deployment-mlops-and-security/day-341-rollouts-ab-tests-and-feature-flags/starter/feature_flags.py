import hashlib
import time
from typing import Dict, Any, List, Optional

class AIFeatureFlagRouter:
    def __init__(self, flag_name: str, canary_percentage: int = 10, shadow_enabled: bool = False):
        self.flag_name = flag_name
        self.canary_pct = max(0, min(100, int(canary_percentage)))
        self.shadow_enabled = bool(shadow_enabled)
        self.shadow_logs: List[Dict[str, Any]] = []

    def get_user_bucket(self, user_id: str) -> int:
        hash_input = f"{self.flag_name}:{user_id}".encode("utf-8")
        hash_hex = hashlib.md5(hash_input).hexdigest()
        return int(hash_hex[:8], 16) % 100

    def route_request(self, user_id: str, prompt: str) -> Dict[str, Any]:
        bucket = self.get_user_bucket(user_id)
        
        if bucket < self.canary_pct:
            live_variant = "CANDIDATE_MODEL_V2"
        else:
            live_variant = "BASELINE_MODEL_V1"

        live_response = f"[{live_variant}] Response for '{prompt}'"
        
        shadow_executed = False
        if self.shadow_enabled:
            shadow_variant = "SHADOW_EXPERIMENTAL_V3"
            shadow_response = f"[{shadow_variant}] Response for '{prompt}'"
            self.shadow_logs.append({
                "user_id": user_id,
                "prompt": prompt,
                "shadow_variant": shadow_variant,
                "shadow_response": shadow_response,
                "timestamp": time.time()
            })
            shadow_executed = True

        return {
            "user_id": user_id,
            "bucket": bucket,
            "assigned_variant": live_variant,
            "response": live_response,
            "shadow_executed": shadow_executed
        }

if __name__ == "__main__":
    r = AIFeatureFlagRouter("test_flag", 20, True)
    print(r.route_request("u1", "hello"))

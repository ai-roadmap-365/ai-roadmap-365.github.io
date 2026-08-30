import math
import time
from typing import Dict, Any, List, Optional

class GPUAutoscalingDecisionEngine:
    def __init__(
        self,
        min_replicas: int = 1,
        max_replicas: int = 10,
        target_waiting_per_pod: int = 5,
        scale_down_cooldown_seconds: int = 300
    ):
        self.min_replicas = int(min_replicas)
        self.max_replicas = int(max_replicas)
        self.target_per_pod = int(target_waiting_per_pod)
        self.cooldown_sec = int(scale_down_cooldown_seconds)
        
        self.current_replicas = int(min_replicas)
        self.idle_since_timestamp: Optional[float] = None
        
    def calculate_desired_replicas(self, waiting_requests: int, current_timestamp: float) -> Dict[str, Any]:
        if waiting_requests <= 0:
            raw_desired = self.min_replicas
        else:
            raw_desired = math.ceil(waiting_requests / self.target_per_pod)
            
        desired = max(self.min_replicas, min(raw_desired, self.max_replicas))
        
        if desired > self.current_replicas:
            self.idle_since_timestamp = None
            old_replicas = self.current_replicas
            self.current_replicas = desired
            return {
                "action": "SCALE_UP",
                "old_replicas": old_replicas,
                "new_replicas": desired,
                "reason": f"Waiting queue ({waiting_requests}) exceeded capacity"
            }
            
        if desired < self.current_replicas:
            if self.idle_since_timestamp is None:
                self.idle_since_timestamp = current_timestamp
                return {
                    "action": "HOLD_COOLDOWN",
                    "current_replicas": self.current_replicas,
                    "desired_replicas": desired,
                    "seconds_in_cooldown": 0.0,
                    "reason": "Queue cleared; waiting for stabilization window"
                }
                
            elapsed = current_timestamp - self.idle_since_timestamp
            if elapsed >= self.cooldown_sec:
                old_replicas = self.current_replicas
                self.current_replicas = desired
                self.idle_since_timestamp = None
                return {
                    "action": "SCALE_DOWN",
                    "old_replicas": old_replicas,
                    "new_replicas": desired,
                    "reason": f"Cooldown window ({self.cooldown_sec}s) expired cleanly"
                }
            else:
                return {
                    "action": "HOLD_COOLDOWN",
                    "current_replicas": self.current_replicas,
                    "desired_replicas": desired,
                    "seconds_in_cooldown": round(elapsed, 1),
                    "reason": f"Stabilization active ({round(self.cooldown_sec - elapsed, 1)}s remaining)"
                }
                
        return {"action": "NO_CHANGE", "current_replicas": self.current_replicas}

if __name__ == "__main__":
    eng = GPUAutoscalingDecisionEngine(min_replicas=1, max_replicas=5, target_waiting_per_pod=5, scale_down_cooldown_seconds=10)
    print(eng.calculate_desired_replicas(20, 100.0))
    print(eng.calculate_desired_replicas(0, 102.0))
    print(eng.calculate_desired_replicas(0, 115.0))

import time
from typing import Dict, Any, List, Optional

class CloudDeploymentOrchestrator:
    def __init__(self):
        self.active_environment = "BLUE"
        self.revisions = {
            "BLUE": {"image_tag": "v1.0.0", "healthy": True, "active_traffic_pct": 100},
            "GREEN": {"image_tag": "v1.0.0", "healthy": False, "active_traffic_pct": 0}
        }
        self.deployment_history: List[Dict[str, Any]] = []

    def deploy_new_revision(self, new_image_tag: str, simulate_health_pass: bool = True) -> Dict[str, Any]:
        target_env = "GREEN" if self.active_environment == "BLUE" else "BLUE"
        current_env = self.active_environment
        
        self.revisions[target_env]["image_tag"] = new_image_tag
        self.revisions[target_env]["healthy"] = False
        
        if simulate_health_pass:
            self.revisions[target_env]["healthy"] = True
            self.revisions[target_env]["active_traffic_pct"] = 100
            self.revisions[current_env]["active_traffic_pct"] = 0
            self.active_environment = target_env
            
            event = {
                "status": "DEPLOYMENT_SUCCESS",
                "active_env": target_env,
                "deployed_image": new_image_tag,
                "timestamp": time.time()
            }
            self.deployment_history.append(event)
            return event
        else:
            self.revisions[target_env]["healthy"] = False
            event = {
                "status": "DEPLOYMENT_FAILED_HEALTH_CHECK",
                "active_env": current_env,
                "rolled_back_to": current_env,
                "timestamp": time.time()
            }
            self.deployment_history.append(event)
            return event

if __name__ == "__main__":
    o = CloudDeploymentOrchestrator()
    print(o.deploy_new_revision("v2.0.0", True))

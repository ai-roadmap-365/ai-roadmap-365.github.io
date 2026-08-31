"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import time
from typing import Dict, Any, List, Optional

class CloudDeploymentOrchestrator:

    def __init__(self):
        self.active_environment = 'BLUE'
        self.revisions = {'BLUE': {'image_tag': 'v1.0.0', 'healthy': True, 'active_traffic_pct': 100}, 'GREEN': {'image_tag': 'v1.0.0', 'healthy': False, 'active_traffic_pct': 0}}
        self.deployment_history: List[Dict[str, Any]] = []

    def deploy_new_revision(self, new_image_tag: str, simulate_health_pass: bool=True) -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement deploy_new_revision.')
if __name__ == '__main__':
    o = CloudDeploymentOrchestrator()
    print(o.deploy_new_revision('v2.0.0', True))

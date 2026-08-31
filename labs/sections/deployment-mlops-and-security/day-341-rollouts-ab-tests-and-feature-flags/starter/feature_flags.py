"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import hashlib
import time
from typing import Dict, Any, List, Optional

class AIFeatureFlagRouter:

    def __init__(self, flag_name: str, canary_percentage: int=10, shadow_enabled: bool=False):
        self.flag_name = flag_name
        self.canary_pct = max(0, min(100, int(canary_percentage)))
        self.shadow_enabled = bool(shadow_enabled)
        self.shadow_logs: List[Dict[str, Any]] = []

    def get_user_bucket(self, user_id: str) -> int:
        raise NotImplementedError('TASK 1: implement get_user_bucket.')

    def route_request(self, user_id: str, prompt: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 2: implement route_request.')
if __name__ == '__main__':
    r = AIFeatureFlagRouter('test_flag', 20, True)
    print(r.route_request('u1', 'hello'))

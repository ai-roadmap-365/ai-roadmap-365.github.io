"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import hashlib
import time
from typing import Dict, Any, Optional, Tuple

class AuthBillingEngine:

    def __init__(self):
        self.tenants: Dict[str, Dict[str, Any]] = {}
        self.active_holds: Dict[str, Dict[str, Any]] = {}

    def register_tenant(self, tenant_id: str, raw_api_key: str, initial_credits: float=10.0, rpm_limit: int=60, tpm_limit: int=100000):
        raise NotImplementedError('TASK 1: implement register_tenant.')

    def authenticate_and_reserve_hold(self, tenant_id: str, raw_api_key: str, estimated_cost: float=0.02, est_tokens: int=500) -> Tuple[bool, str, Optional[str]]:
        raise NotImplementedError('TASK 2: implement authenticate_and_reserve_hold.')

    def settle_token_usage(self, hold_id: str, prompt_tokens: int, completion_tokens: int) -> Dict[str, Any]:
        raise NotImplementedError('TASK 3: implement settle_token_usage.')
if __name__ == '__main__':
    engine = AuthBillingEngine()
    engine.register_tenant('org_1', 'key123', 5.0)
    print(engine.authenticate_and_reserve_hold('org_1', 'key123', 0.02))

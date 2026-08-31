"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple

class FullStackAIAppEngine:

    def __init__(self):
        self.tenants: Dict[str, Dict[str, Any]] = {'tenant_alpha': {'key_hash': hashlib.sha256(b'sk_alpha_123').hexdigest(), 'balance': 10.0, 'reserved_holds': 0.0, 'rpm_limit': 60, 'requests_this_min': 0, 'last_reset': time.time()}, 'tenant_poor': {'key_hash': hashlib.sha256(b'sk_poor_123').hexdigest(), 'balance': 0.01, 'reserved_holds': 0.0, 'rpm_limit': 10, 'requests_this_min': 0, 'last_reset': time.time()}}
        self.cache: Dict[str, str] = {}
        self.active_holds: Dict[str, Dict[str, Any]] = {}
        self.providers = ['primary_claude', 'secondary_openai', 'backup_vllm']

    def process_chat_request(self, tenant_id: str, raw_key: str, prompt: str, simulated_failing_providers: Optional[List[str]]=None) -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement process_chat_request.')
if __name__ == '__main__':
    app = FullStackAIAppEngine()
    print('Normal:', app.process_chat_request('tenant_alpha', 'sk_alpha_123', 'Hi'))

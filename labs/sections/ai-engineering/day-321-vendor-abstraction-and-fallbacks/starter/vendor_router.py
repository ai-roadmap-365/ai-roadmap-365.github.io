"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import time
from typing import Dict, Any, List, Optional

class VendorFallbackRouter:

    def __init__(self):
        self.providers: Dict[str, Dict[str, Any]] = {'anthropic': {'name': 'Anthropic Claude 3.5', 'healthy': True, 'consecutive_fails': 0}, 'openai': {'name': 'OpenAI GPT-4o', 'healthy': True, 'consecutive_fails': 0}, 'vllm_local': {'name': 'Self-Hosted Llama 3.3', 'healthy': True, 'consecutive_fails': 0}}
        self.priority_order = ['anthropic', 'openai', 'vllm_local']

    def set_provider_health(self, provider_id: str, healthy: bool):
        raise NotImplementedError('TASK 1: implement set_provider_health.')

    def call_model_with_fallback(self, prompt: str, simulated_failing_providers: Optional[List[str]]=None) -> Dict[str, Any]:
        raise NotImplementedError('TASK 2: implement call_model_with_fallback.')
if __name__ == '__main__':
    router = VendorFallbackRouter()
    print('Normal:', router.call_model_with_fallback('Hello'))

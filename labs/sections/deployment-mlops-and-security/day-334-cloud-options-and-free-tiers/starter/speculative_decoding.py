"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

from typing import Dict, Any, List, Tuple, Optional

class SpeculativeDecodingEngine:

    def __init__(self, acceptance_probability_bias: float=0.8):
        self.alpha_bias = float(acceptance_probability_bias)
        self.prefix_cache: Dict[str, str] = {}

    def register_prefix_cache(self, prefix_key: str, cached_kv_id: str):
        raise NotImplementedError('TASK 1: implement register_prefix_cache.')

    def lookup_prefix(self, prompt: str) -> Tuple[bool, str]:
        raise NotImplementedError('TASK 2: implement lookup_prefix.')

    def execute_speculative_step(self, draft_tokens: List[str], target_ground_truth: List[str]) -> Dict[str, Any]:
        raise NotImplementedError('TASK 3: implement execute_speculative_step.')
if __name__ == '__main__':
    eng = SpeculativeDecodingEngine()
    eng.register_prefix_cache('System Prompt', 'kv_0')
    print(eng.lookup_prefix('System Prompt: do task'))
    print(eng.execute_speculative_step(['a', 'b'], ['a', 'b', 'c']))

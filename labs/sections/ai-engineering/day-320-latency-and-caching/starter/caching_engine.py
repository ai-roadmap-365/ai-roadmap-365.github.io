"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple

class MultiTierLLMCache:

    def __init__(self, semantic_similarity_threshold: float=0.85, default_ttl_seconds: float=300.0):
        self.exact_cache: Dict[str, Dict[str, Any]] = {}
        self.semantic_cache: List[Dict[str, Any]] = []
        self.similarity_threshold = float(semantic_similarity_threshold)
        self.ttl = float(default_ttl_seconds)

    @staticmethod
    def _compute_hash(text: str) -> str:
        raise NotImplementedError('TASK 1: implement _compute_hash.')

    @staticmethod
    def _mock_embedding(text: str, dim: int=16) -> List[float]:
        raise NotImplementedError('TASK 2: implement _mock_embedding.')

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        raise NotImplementedError('TASK 3: implement _cosine_similarity.')

    def get(self, query: str) -> Tuple[Optional[str], str]:
        raise NotImplementedError('TASK 4: implement get.')

    def put(self, query: str, response: str):
        raise NotImplementedError('TASK 5: implement put.')
if __name__ == '__main__':
    cache = MultiTierLLMCache()
    cache.put('Hello world', 'Hi there!')
    print(cache.get('Hello world'))

import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple

class MultiTierLLMCache:
    def __init__(self, semantic_similarity_threshold: float = 0.85, default_ttl_seconds: float = 300.0):
        self.exact_cache: Dict[str, Dict[str, Any]] = {}
        self.semantic_cache: List[Dict[str, Any]] = []
        self.similarity_threshold = float(semantic_similarity_threshold)
        self.ttl = float(default_ttl_seconds)
        
    @staticmethod
    def _compute_hash(text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode()).hexdigest()

    @staticmethod
    def _mock_embedding(text: str, dim: int = 16) -> List[float]:
        vec = [0.0] * dim
        words = text.lower().split()
        for w in words:
            h = sum(ord(c) for c in w) % dim
            vec[h] += 1.0
        return vec

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return round(dot / (norm1 * norm2), 4)

    def get(self, query: str) -> Tuple[Optional[str], str]:
        now = time.time()
        
        q_hash = self._compute_hash(query)
        if q_hash in self.exact_cache:
            entry = self.exact_cache[q_hash]
            if now - entry["timestamp"] <= self.ttl:
                return entry["response"], "TIER_1_EXACT_HIT"
                
        q_vec = self._mock_embedding(query)
        for entry in self.semantic_cache:
            if now - entry["timestamp"] <= self.ttl:
                sim = self._cosine_similarity(q_vec, entry["embedding"])
                if sim >= self.similarity_threshold:
                    return entry["response"], f"TIER_2_SEMANTIC_HIT (sim={sim})"
                    
        return None, "CACHE_MISS"

    def put(self, query: str, response: str):
        now = time.time()
        q_hash = self._compute_hash(query)
        q_vec = self._mock_embedding(query)
        
        self.exact_cache[q_hash] = {
            "response": response,
            "timestamp": now
        }
        
        self.semantic_cache.append({
            "query": query,
            "embedding": q_vec,
            "response": response,
            "timestamp": now
        })

if __name__ == "__main__":
    cache = MultiTierLLMCache()
    cache.put("Hello world", "Hi there!")
    print(cache.get("Hello world"))

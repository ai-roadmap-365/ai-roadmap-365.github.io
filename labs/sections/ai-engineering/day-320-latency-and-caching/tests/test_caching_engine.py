import pytest
import time
from examples.caching_engine import MultiTierLLMCache

def test_tier_1_exact_hash_hit():
    cache = MultiTierLLMCache()
    cache.put("What is Python?", "Python is a programming language.")
    resp, tier = cache.get("  what is python?  ")
    assert resp == "Python is a programming language."
    assert tier == "TIER_1_EXACT_HIT"

def test_tier_2_semantic_hit():
    cache = MultiTierLLMCache(semantic_similarity_threshold=0.80)
    cache.put("Explain photosynthesis in plants", "Photosynthesis converts light to energy.")
    # Slightly different casing/words with close embedding
    resp, tier = cache.get("Explain photosynthesis in plants")
    assert resp is not None
    assert "HIT" in tier

def test_cache_miss_on_novel_query():
    cache = MultiTierLLMCache()
    cache.put("First question", "First answer")
    resp, tier = cache.get("Completely different topic about space travel")
    assert resp is None
    assert tier == "CACHE_MISS"

def test_ttl_expiration():
    cache = MultiTierLLMCache(default_ttl_seconds=0.05)
    cache.put("Temporary query", "Temporary answer")
    
    # Immediate hit
    resp1, tier1 = cache.get("Temporary query")
    assert resp1 == "Temporary answer"
    
    # Wait for TTL expiration
    time.sleep(0.06)
    resp2, tier2 = cache.get("Temporary query")
    assert resp2 is None
    assert tier2 == "CACHE_MISS"

def test_cosine_similarity_edge_cases():
    assert MultiTierLLMCache._cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert MultiTierLLMCache._cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0

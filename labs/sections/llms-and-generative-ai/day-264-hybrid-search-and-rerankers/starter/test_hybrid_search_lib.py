import pytest
from examples.hybrid_search_lib import (
    HybridSearchEngine
)

def test_bm25_exact_keyword_matching():
    engine = HybridSearchEngine()
    docs = [
        {"id": 0, "text": "fatal error 504 gateway timeout"},
        {"id": 1, "text": "normal server response ok"},
        {"id": 2, "text": "database migration in progress"}
    ]
    engine.index_documents(docs)
    results = engine.bm25_search("fatal error", top_k=1)
    
    assert len(results) == 1
    assert results[0][0] == 0
    assert results[0][1] > 0.0

def test_reciprocal_rank_fusion_logic():
    engine = HybridSearchEngine(rrf_k=60)
    engine.documents = [{"id": 0}, {"id": 1}, {"id": 2}]
    sparse = [(0, 10.5), (1, 5.2)]
    dense = [(1, 0.95), (0, 0.85)]
    
    # Doc 0: 1/61 + 1/62 = 0.01639 + 0.01612 = 0.0325
    # Doc 1: 1/62 + 1/61 = 0.0325
    results = engine.reciprocal_rank_fusion(sparse, dense, top_k=2)
    assert len(results) == 2
    assert results[0][1] > 0.03

def test_empty_query_bm25():
    engine = HybridSearchEngine()
    docs = [{"id": 0, "text": "hello world"}]
    engine.index_documents(docs)
    results = engine.bm25_search("unmatched term", top_k=1)
    assert results[0][1] == 0.0

def test_rrf_top_k_bounds():
    engine = HybridSearchEngine()
    engine.documents = [{"id": i} for i in range(10)]
    sparse = [(i, 1.0) for i in range(10)]
    dense = [(i, 1.0) for i in range(10)]
    results = engine.reciprocal_rank_fusion(sparse, dense, top_k=3)
    assert len(results) == 3

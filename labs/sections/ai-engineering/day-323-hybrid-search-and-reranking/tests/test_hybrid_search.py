import pytest
from examples.hybrid_search import HybridSearchEngine

def test_index_and_bm25_scoring():
    engine = HybridSearchEngine()
    docs = [
        {"id": "d1", "text": "apple banana cherry"},
        {"id": "d2", "text": "dog elephant fox"},
        {"id": "d3", "text": "apple dog giraffe"}
    ]
    engine.index_documents(docs)
    s1 = engine._bm25_score("apple", "apple banana cherry")
    s2 = engine._bm25_score("apple", "dog elephant fox")
    assert s1 > s2
    assert s2 == 0.0

def test_dense_similarity():
    engine = HybridSearchEngine()
    sim = engine._dense_sim("machine learning", "machine learning in python")
    assert sim == 1.0
    sim_none = engine._dense_sim("rocket", "cooking recipe soup")
    assert sim_none == 0.0

def test_rrf_fusion_ordering():
    engine = HybridSearchEngine(rrf_k=60)
    docs = [
        {"id": "d1", "text": "Database indexing and B-tree optimization in PostgreSQL."},
        {"id": "d2", "text": "PostgreSQL error ERR_INDEX_CORRUPT during vacuum."},
        {"id": "d3", "text": "Baking chocolate chip cookies in an oven."}
    ]
    engine.index_documents(docs)
    res = engine.search_hybrid("ERR_INDEX_CORRUPT PostgreSQL", top_k=2)
    assert len(res) == 2
    # Exact keyword match d2 should rank #1
    assert res[0]["doc_id"] == "d2"
    assert res[0]["rrf_score"] > res[1]["rrf_score"]

def test_empty_documents_handling():
    engine = HybridSearchEngine()
    res = engine.search_hybrid("test query")
    assert res == []

def test_rrf_math_formula():
    engine = HybridSearchEngine(rrf_k=60)
    # rank 1 + rank 1 = 1/61 + 1/61 = 2/61 ~ 0.032787
    expected = (1.0 / 61.0) + (1.0 / 61.0)
    docs = [{"id": "single", "text": "only document in index"}]
    engine.index_documents(docs)
    res = engine.search_hybrid("only document")
    assert pytest.approx(res[0]["rrf_score"], 0.0001) == expected

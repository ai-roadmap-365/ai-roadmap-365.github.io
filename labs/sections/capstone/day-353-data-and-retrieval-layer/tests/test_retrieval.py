import pytest
from examples.retrieval import HybridRetrievalEngine

@pytest.fixture
def populated_engine():
    engine = HybridRetrievalEngine(rrf_k=60)
    engine.ingest_document("doc1", "Python programming language for machine learning.", [0.9, 0.1, 0.0], {"topic": "ai"})
    engine.ingest_document("doc2", "Exact error code 0xDEADBEEF during network connection.", [0.1, 0.8, 0.1], {"topic": "sys"})
    engine.ingest_document("doc3", "Cloud container deployment with Docker and Kubernetes.", [0.2, 0.2, 0.9], {"topic": "infra"})
    return engine

def test_idempotent_ingestion(populated_engine):
    # Attempt duplicate insert
    dup = populated_engine.ingest_document("doc1_dup", "Python programming language for machine learning.", [0.9, 0.1, 0.0])
    assert dup is False
    assert len(populated_engine.documents) == 3

def test_sparse_bm25_exact_keyword_lookup(populated_engine):
    res = populated_engine.search_hybrid("0xDEADBEEF", [0.0, 0.0, 0.0], top_k=1)
    assert len(res) == 1
    assert res[0]["id"] == "doc2"

def test_dense_semantic_lookup(populated_engine):
    res = populated_engine.search_hybrid("deep neural networks", [0.85, 0.12, 0.05], top_k=1)
    assert len(res) == 1
    assert res[0]["id"] == "doc1"

def test_rrf_rank_fusion(populated_engine):
    # Query matching both keyword in doc3 and semantic in doc1
    res = populated_engine.search_hybrid("kubernetes clusters", [0.25, 0.15, 0.85], top_k=3)
    assert res[0]["id"] == "doc3"
    assert "rrf_score" in res[0]
    assert res[0]["rrf_score"] > 0.0

def test_top_k_limiting_and_metadata(populated_engine):
    res = populated_engine.search_hybrid("machine learning and kubernetes", [0.5, 0.1, 0.5], top_k=2)
    assert len(res) == 2
    assert "metadata" in res[0]

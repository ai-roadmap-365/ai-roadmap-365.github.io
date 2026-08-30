import pytest
import numpy as np
from examples.semantic_similarity_search_lib import (
    ExactKNNSearchEngine
)

def test_exact_knn_search():
    engine = ExactKNNSearchEngine(dimension=3)
    vecs = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.9, 0.1, 0.0]
    ], dtype=np.float32)
    metas = [{"doc_id": "doc1"}, {"doc_id": "doc2"}, {"doc_id": "doc3"}]
    engine.add_documents(vecs, metas)

    query = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    results = engine.search(query, top_k=2)

    assert len(results) == 2
    assert results[0][0]["doc_id"] == "doc1"
    assert np.isclose(results[0][1], 1.0)
    assert results[1][0]["doc_id"] == "doc3"

def test_filtered_search():
    engine = ExactKNNSearchEngine(dimension=2)
    vecs = np.array([
        [1.0, 0.0],
        [0.9, 0.1],
        [0.0, 1.0]
    ], dtype=np.float32)
    metas = [
        {"id": 0, "tag": "prod"},
        {"id": 1, "tag": "dev"},
        {"id": 2, "tag": "prod"}
    ]
    engine.add_documents(vecs, metas)

    query = np.array([1.0, 0.0], dtype=np.float32)
    # Search only 'dev' tag
    results = engine.search_with_filter(query, filter_key="tag", filter_val="dev", top_k=5)
    assert len(results) == 1
    assert results[0][0]["id"] == 1

def test_empty_engine_handling():
    engine = ExactKNNSearchEngine(dimension=4)
    query = np.array([1.0, 0.0, 0.0, 0.0])
    results = engine.search(query, top_k=5)
    assert results == []

def test_top_k_larger_than_corpus():
    engine = ExactKNNSearchEngine(dimension=2)
    vecs = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    metas = [{"id": 0}, {"id": 1}]
    engine.add_documents(vecs, metas)

    query = np.array([1.0, 1.0])
    results = engine.search(query, top_k=10)
    assert len(results) == 2

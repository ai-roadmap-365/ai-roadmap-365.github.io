import pytest
import numpy as np
from examples.vector_databases_lib import (
    SimpleNSWIndex
)

def test_nsw_index_basic_retrieval():
    index = SimpleNSWIndex(dimension=3, max_neighbors=3)
    v0 = np.array([1.0, 0.0, 0.0])
    v1 = np.array([0.95, 0.05, 0.0])
    v2 = np.array([0.0, 1.0, 0.0])
    index.add_document(v0, {"id": 0})
    index.add_document(v1, {"id": 1})
    index.add_document(v2, {"id": 2})

    query = np.array([1.0, 0.0, 0.0])
    results = index.search(query, top_k=2, ef_search=5)
    
    assert len(results) == 2
    assert results[0][0]["id"] == 0
    assert results[1][0]["id"] == 1

def test_nsw_graph_connectivity():
    index = SimpleNSWIndex(dimension=4, max_neighbors=3)
    for i in range(10):
        vec = np.random.randn(4)
        index.add_document(vec, {"id": i})

    # Assert all nodes are in graph
    for i in range(10):
        assert i in index.graph
        assert len(index.graph[i]) > 0 or i == 0

def test_empty_nsw_index():
    index = SimpleNSWIndex(dimension=4)
    query = np.array([1.0, 0.0, 0.0, 0.0])
    results = index.search(query, top_k=3)
    assert results == []

def test_ef_search_recall_scaling():
    index = SimpleNSWIndex(dimension=4, max_neighbors=4)
    for i in range(20):
        vec = np.random.randn(4)
        index.add_document(vec, {"id": i})

    query = np.random.randn(4)
    res_low = index.search(query, top_k=3, ef_search=3)
    res_high = index.search(query, top_k=3, ef_search=15)
    
    assert len(res_low) <= 3
    assert len(res_high) == 3

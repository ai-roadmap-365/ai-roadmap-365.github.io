import pytest
import numpy as np
from examples.what_embeddings_are_lib import (
    VectorSimilarityEngine
)

def test_normalization_and_cosine_similarity():
    engine = VectorSimilarityEngine(normalize=True)
    v1 = np.array([3.0, 4.0])
    norm_v1 = engine.l2_normalize(v1)
    
    assert np.isclose(np.linalg.norm(norm_v1), 1.0)
    assert np.isclose(norm_v1[0], 0.6)
    assert np.isclose(norm_v1[1], 0.8)

    # Identical vectors should have cosine similarity 1.0
    assert np.isclose(engine.cosine_similarity(v1, v1), 1.0)

    # Orthogonal vectors should have cosine similarity 0.0
    v_ortho = np.array([-4.0, 3.0])
    assert np.isclose(engine.cosine_similarity(v1, v_ortho), 0.0)

def test_document_ranking():
    engine = VectorSimilarityEngine(normalize=True)
    query = np.array([1.0, 0.0, 0.0])
    
    doc0 = np.array([0.9, 0.1, 0.0]) # High similarity
    doc1 = np.array([0.0, 1.0, 0.0]) # Zero similarity (orthogonal)
    doc2 = np.array([0.5, 0.5, 0.0]) # Medium similarity

    ranked = engine.rank_documents(query, [doc0, doc1, doc2])
    assert ranked[0][0] == 0
    assert ranked[1][0] == 2
    assert ranked[2][0] == 1

def test_euclidean_distance():
    engine = VectorSimilarityEngine(normalize=True)
    p1 = np.array([0.0, 0.0])
    p2 = np.array([3.0, 4.0])
    assert np.isclose(engine.euclidean_distance(p1, p2), 5.0)

def test_matryoshka_truncation():
    engine = VectorSimilarityEngine(normalize=True)
    vec = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    truncated = engine.matryoshka_truncate(vec, target_dim=3)
    
    assert len(truncated) == 3
    assert np.isclose(np.linalg.norm(truncated), 1.0)

import numpy as np
from typing import List, Tuple

class VectorSimilarityEngine:
    def __init__(self, normalize: bool = True):
        self.normalize = normalize

    def l2_normalize(self, v: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(v)
        if norm == 0:
            return v
        return v / norm

    def cosine_similarity(self, u: np.ndarray, v: np.ndarray) -> float:
        norm_u = self.l2_normalize(u) if self.normalize else u
        norm_v = self.l2_normalize(v) if self.normalize else v
        return float(np.dot(norm_u, norm_v))

    def euclidean_distance(self, u: np.ndarray, v: np.ndarray) -> float:
        return float(np.linalg.norm(u - v))

    def rank_documents(self, query_vec: np.ndarray, doc_vecs: List[np.ndarray]) -> List[Tuple[int, float]]:
        scores = []
        for idx, doc_vec in enumerate(doc_vecs):
            sim = self.cosine_similarity(query_vec, doc_vec)
            scores.append((idx, sim))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def matryoshka_truncate(self, v: np.ndarray, target_dim: int) -> np.ndarray:
        truncated = v[:target_dim]
        return self.l2_normalize(truncated)

def run_embeddings_demo():
    engine = VectorSimilarityEngine(normalize=True)
    v1 = np.array([1.0, 2.0, 3.0])
    v2 = np.array([1.0, 2.0, 3.0])
    sim = engine.cosine_similarity(v1, v2)
    dist = engine.euclidean_distance(v1, v2)
    print(f"Embeddings Demo Executed. Cosine Sim: {sim:.4f}, L2 Dist: {dist:.4f}")
    return sim, dist

if __name__ == "__main__":
    run_embeddings_demo()

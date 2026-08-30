import numpy as np
from typing import List, Dict, Any, Tuple

class ExactKNNSearchEngine:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.vectors: np.ndarray = np.empty((0, dimension), dtype=np.float32)
        self.metadata: List[Dict[str, Any]] = []

    def add_documents(self, vectors: np.ndarray, metadatas: List[Dict[str, Any]]) -> None:
        if len(vectors) == 0:
            return
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized_vecs = vectors / norms
        
        self.vectors = np.vstack([self.vectors, normalized_vecs]) if self.vectors.size else normalized_vecs
        self.metadata.extend(metadatas)

    def search(self, query_vec: np.ndarray, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        if len(self.vectors) == 0:
            return []
        
        q_norm = np.linalg.norm(query_vec)
        q_unit = query_vec / (q_norm if q_norm > 0 else 1.0)

        scores = np.dot(self.vectors, q_unit)
        k = min(top_k, len(scores))
        
        if k == len(scores):
            top_indices = np.argsort(scores)[::-1]
        else:
            partition_idx = np.argpartition(scores, -k)[-k:]
            top_indices = partition_idx[np.argsort(scores[partition_idx])[::-1]]

        return [(self.metadata[idx], float(scores[idx])) for idx in top_indices]

    def search_with_filter(self, query_vec: np.ndarray, filter_key: str, filter_val: Any, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        matching_indices = [
            idx for idx, meta in enumerate(self.metadata)
            if meta.get(filter_key) == filter_val
        ]
        if not matching_indices:
            return []
        
        sub_vectors = self.vectors[matching_indices]
        q_norm = np.linalg.norm(query_vec)
        q_unit = query_vec / (q_norm if q_norm > 0 else 1.0)
        
        scores = np.dot(sub_vectors, q_unit)
        k = min(top_k, len(scores))
        
        if k == len(scores):
            top_sub_indices = np.argsort(scores)[::-1]
        else:
            partition_idx = np.argpartition(scores, -k)[-k:]
            top_sub_indices = partition_idx[np.argsort(scores[partition_idx])[::-1]]

        return [(self.metadata[matching_indices[idx]], float(scores[idx])) for idx in top_sub_indices]

def run_knn_demo():
    engine = ExactKNNSearchEngine(dimension=4)
    vecs = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.7, 0.7, 0.0, 0.0]
    ], dtype=np.float32)
    metas = [{"id": 0, "cat": "A"}, {"id": 1, "cat": "B"}, {"id": 2, "cat": "A"}]
    engine.add_documents(vecs, metas)
    
    query = np.array([1.0, 0.1, 0.0, 0.0], dtype=np.float32)
    results = engine.search(query, top_k=2)
    print(f"k-NN Demo Executed. Top Match: {results[0][0]['id']} with score {results[0][1]:.4f}")
    return results

if __name__ == "__main__":
    run_knn_demo()

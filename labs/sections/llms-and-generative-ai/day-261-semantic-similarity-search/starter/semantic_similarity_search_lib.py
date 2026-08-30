import numpy as np
from typing import List, Dict, Any, Tuple

class ExactKNNSearchEngine:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.vectors: np.ndarray = np.empty((0, dimension), dtype=np.float32)
        self.metadata: List[Dict[str, Any]] = []

    def add_documents(self, vectors: np.ndarray, metadatas: List[Dict[str, Any]]) -> None:
        # TODO: Add and L2-normalize document vectors
        pass

    def search(self, query_vec: np.ndarray, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        # TODO: Vectorized dot product and Top-K retrieval
        pass

    def search_with_filter(self, query_vec: np.ndarray, filter_key: str, filter_val: Any, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        # TODO: Metadata pre-filtering followed by exact search
        pass

import math
from collections import Counter
from typing import List, Dict, Any, Tuple

class HybridSearchEngine:
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self.documents: List[Dict[str, Any]] = []

    def index_documents(self, docs: List[Dict[str, Any]]):
        # TODO: Compute term frequencies, document lengths, and IDF
        pass

    def bm25_search(self, query: str, top_k: int = 10, k1: float = 1.5, b: float = 0.75) -> List[Tuple[int, float]]:
        # TODO: Calculate BM25 scores
        pass

    def reciprocal_rank_fusion(self, sparse_results: List[Tuple[int, float]], dense_results: List[Tuple[int, float]], top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        # TODO: Merge rankings using RRF formulation: 1 / (k + rank)
        pass

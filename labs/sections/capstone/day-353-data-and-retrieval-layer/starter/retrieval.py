"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import math
import hashlib
import re
from typing import List, Dict, Any, Tuple

class HybridRetrievalEngine:

    def __init__(self, rrf_k: int=60):
        self.rrf_k = rrf_k
        self.documents: List[Dict[str, Any]] = []
        self.doc_hashes: set = set()
        self.dense_embeddings: List[List[float]] = []
        self.inverted_index: Dict[str, List[int]] = {}
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0

    def _tokenize(self, text: str) -> List[str]:
        raise NotImplementedError('TASK 1: implement _tokenize.')

    def ingest_document(self, doc_id: str, text: str, embedding: List[float], metadata: Dict[str, Any]=None) -> bool:
        raise NotImplementedError('TASK 2: implement ingest_document.')

    def _score_bm25(self, query_tokens: List[str], k1: float=1.5, b: float=0.75) -> List[Tuple[int, float]]:
        raise NotImplementedError('TASK 3: implement _score_bm25.')

    def _score_dense(self, query_embedding: List[float]) -> List[Tuple[int, float]]:
        raise NotImplementedError('TASK 4: implement _score_dense.')

    def search_hybrid(self, query_text: str, query_embedding: List[float], top_k: int=5) -> List[Dict[str, Any]]:
        raise NotImplementedError('TASK 5: implement search_hybrid.')
if __name__ == '__main__':
    engine = HybridRetrievalEngine()
    engine.ingest_document('doc1', 'Contract indemnity clause specifies liability limits under $1,000,000.', [0.8, 0.1, 0.3])
    engine.ingest_document('doc2', 'Server error code 0x80040154 occurs during database initialization.', [0.1, 0.9, 0.2])
    print(engine.search_hybrid('indemnity liability limits', [0.75, 0.15, 0.28], top_k=2))

import math
from collections import Counter
from typing import List, Dict, Any, Tuple

class HybridSearchEngine:
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self.documents: List[Dict[str, Any]] = []
        self.doc_term_freqs: List[Counter] = []
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0
        self.idf: Dict[str, float] = {}

    def index_documents(self, docs: List[Dict[str, Any]]):
        self.documents = docs
        self.doc_term_freqs = []
        self.doc_lengths = []
        df: Counter = Counter()

        for doc in docs:
            tokens = doc["text"].lower().split()
            tf = Counter(tokens)
            self.doc_term_freqs.append(tf)
            self.doc_lengths.append(len(tokens))
            for term in tf.keys():
                df[term] += 1

        n_docs = len(docs)
        self.avg_doc_len = sum(self.doc_lengths) / max(1, n_docs)
        self.idf = {term: math.log((n_docs - count + 0.5) / (count + 0.5) + 1.0) for term, count in df.items()}

    def bm25_search(self, query: str, top_k: int = 10, k1: float = 1.5, b: float = 0.75) -> List[Tuple[int, float]]:
        q_tokens = query.lower().split()
        scores = []

        for idx, tf in enumerate(self.doc_term_freqs):
            score = 0.0
            d_len = self.doc_lengths[idx]
            for term in q_tokens:
                if term in tf:
                    term_idf = self.idf.get(term, 0.0)
                    freq = tf[term]
                    numerator = freq * (k1 + 1.0)
                    denominator = freq + k1 * (1.0 - b + b * (d_len / self.avg_doc_len))
                    score += term_idf * (numerator / denominator)
            scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def reciprocal_rank_fusion(self, sparse_results: List[Tuple[int, float]], dense_results: List[Tuple[int, float]], top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        rrf_scores: Dict[int, float] = Counter()

        for rank, (doc_idx, _) in enumerate(sparse_results):
            rrf_scores[doc_idx] += 1.0 / (self.rrf_k + (rank + 1))

        for rank, (doc_idx, _) in enumerate(dense_results):
            rrf_scores[doc_idx] += 1.0 / (self.rrf_k + (rank + 1))

        ranked_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return [(self.documents[doc_idx], score) for doc_idx, score in ranked_items[:top_k]]

def run_hybrid_demo():
    engine = HybridSearchEngine()
    docs = [
        {"id": 0, "text": "Error 504 Gateway Timeout on API gateway"},
        {"id": 1, "text": "Latency optimization and server sluggish performance tuning"},
        {"id": 2, "text": "Database indexing and Postgres connection pool configuration"}
    ]
    engine.index_documents(docs)
    sparse_res = engine.bm25_search("error 504 gateway", top_k=2)
    dense_res = [(1, 0.95), (0, 0.82)]
    hybrid_res = engine.reciprocal_rank_fusion(sparse_res, dense_res, top_k=2)
    print(f"Hybrid Demo Executed. Top Match: {hybrid_res[0][0]['text']} with RRF score {hybrid_res[0][1]:.4f}")
    return hybrid_res

if __name__ == "__main__":
    run_hybrid_demo()

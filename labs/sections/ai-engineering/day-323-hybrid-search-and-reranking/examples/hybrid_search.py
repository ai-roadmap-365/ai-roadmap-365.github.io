import math
from typing import Dict, Any, List, Tuple
from collections import Counter

class HybridSearchEngine:
    def __init__(self, rrf_k: int = 60):
        self.documents: List[Dict[str, Any]] = []
        self.doc_freqs: Counter = Counter()
        self.avg_doc_len: float = 0.0
        self.rrf_k = int(rrf_k)
        
    def index_documents(self, docs: List[Dict[str, Any]]):
        self.documents = docs
        total_len = 0
        self.doc_freqs = Counter()
        for doc in docs:
            words = set(doc["text"].lower().split())
            self.doc_freqs.update(words)
            total_len += len(doc["text"].split())
        self.avg_doc_len = total_len / max(1, len(docs))
        
    def _bm25_score(self, query: str, doc_text: str) -> float:
        k1 = 1.5
        b = 0.75
        q_words = query.lower().split()
        d_words = doc_text.lower().split()
        d_len = len(d_words)
        doc_word_counts = Counter(d_words)
        
        score = 0.0
        n_docs = len(self.documents)
        
        for qw in q_words:
            if qw not in doc_word_counts:
                continue
            tf = doc_word_counts[qw]
            df = self.doc_freqs.get(qw, 0)
            idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (d_len / max(1.0, self.avg_doc_len)))
            score += idf * (numerator / denominator)
        return round(score, 4)

    def _dense_sim(self, query: str, doc_text: str) -> float:
        q_words = set(query.lower().split())
        d_words = set(doc_text.lower().split())
        overlap = len(q_words.intersection(d_words))
        return round(overlap / max(1, len(q_words)), 4)

    def search_hybrid(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.documents:
            return []
            
        bm25_scored = []
        for i, doc in enumerate(self.documents):
            s = self._bm25_score(query, doc["text"])
            bm25_scored.append((i, s))
        bm25_scored.sort(key=lambda x: x[1], reverse=True)
        bm25_ranks = {doc_idx: rank + 1 for rank, (doc_idx, _) in enumerate(bm25_scored)}
        
        dense_scored = []
        for i, doc in enumerate(self.documents):
            s = self._dense_sim(query, doc["text"])
            dense_scored.append((i, s))
        dense_scored.sort(key=lambda x: x[1], reverse=True)
        dense_ranks = {doc_idx: rank + 1 for rank, (doc_idx, _) in enumerate(dense_scored)}
        
        fused_scores: Dict[int, float] = {}
        for i in range(len(self.documents)):
            r_bm25 = bm25_ranks[i]
            r_dense = dense_ranks[i]
            rrf_val = (1.0 / (self.rrf_k + r_bm25)) + (1.0 / (self.rrf_k + r_dense))
            fused_scores[i] = rrf_val
            
        ranked_indices = sorted(fused_scores.keys(), key=lambda idx: fused_scores[idx], reverse=True)
        
        results = []
        for idx in ranked_indices[:top_k]:
            results.append({
                "doc_id": self.documents[idx]["id"],
                "text": self.documents[idx]["text"],
                "rrf_score": round(fused_scores[idx], 6),
                "bm25_rank": bm25_ranks[idx],
                "dense_rank": dense_ranks[idx]
            })
        return results

if __name__ == "__main__":
    docs = [
        {"id": "doc_1", "text": "Kubernetes cluster container deployment configuration."},
        {"id": "doc_2", "text": "Return policy: 30 days full refund on electronics."},
        {"id": "doc_3", "text": "Error ERR_403_FORBIDDEN occurs when authentication credentials expire."}
    ]
    engine = HybridSearchEngine()
    engine.index_documents(docs)
    print(engine.search_hybrid("ERR_403_FORBIDDEN error"))

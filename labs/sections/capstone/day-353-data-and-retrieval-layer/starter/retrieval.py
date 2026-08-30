import math
import hashlib
import re
from typing import List, Dict, Any, Tuple

class HybridRetrievalEngine:
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self.documents: List[Dict[str, Any]] = []
        self.doc_hashes: set = set()
        self.dense_embeddings: List[List[float]] = []
        
        self.inverted_index: Dict[str, List[int]] = {}
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())

    def ingest_document(self, doc_id: str, text: str, embedding: List[float], metadata: Dict[str, Any] = None) -> bool:
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if content_hash in self.doc_hashes:
            return False

        self.doc_hashes.add(content_hash)
        idx = len(self.documents)
        tokens = self._tokenize(text)
        
        self.documents.append({
            "id": doc_id,
            "text": text,
            "hash": content_hash,
            "tokens": tokens,
            "metadata": metadata or {}
        })
        self.dense_embeddings.append(embedding)
        self.doc_lengths.append(len(tokens))

        for tok in set(tokens):
            if tok not in self.inverted_index:
                self.inverted_index[tok] = []
            self.inverted_index[tok].append(idx)

        self.avg_doc_len = sum(self.doc_lengths) / len(self.doc_lengths)
        return True

    def _score_bm25(self, query_tokens: List[str], k1: float = 1.5, b: float = 0.75) -> List[Tuple[int, float]]:
        scores = {}
        N = len(self.documents)
        for tok in query_tokens:
            if tok not in self.inverted_index:
                continue
            df = len(self.inverted_index[tok])
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1.0)
            
            for doc_idx in self.inverted_index[tok]:
                tf = self.documents[doc_idx]["tokens"].count(tok)
                doc_len = self.doc_lengths[doc_idx]
                numerator = tf * (k1 + 1.0)
                denominator = tf + k1 * (1.0 - b + b * (doc_len / (self.avg_doc_len or 1.0)))
                score = idf * (numerator / denominator)
                scores[doc_idx] = scores.get(doc_idx, 0.0) + score
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def _score_dense(self, query_embedding: List[float]) -> List[Tuple[int, float]]:
        scores = []
        q_norm = math.sqrt(sum(x * x for x in query_embedding)) or 1.0
        for idx, emb in enumerate(self.dense_embeddings):
            dot = sum(q * e for q, e in zip(query_embedding, emb))
            e_norm = math.sqrt(sum(e * e for e in emb)) or 1.0
            cosine = dot / (q_norm * e_norm)
            scores.append((idx, cosine))
        return sorted(scores, key=lambda x: x[1], reverse=True)

    def search_hybrid(self, query_text: str, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        query_tokens = self._tokenize(query_text)
        sparse_ranked = self._score_bm25(query_tokens)
        dense_ranked = self._score_dense(query_embedding)

        rrf_scores: Dict[int, float] = {}
        for rank, (doc_idx, _) in enumerate(sparse_ranked):
            rrf_scores[doc_idx] = rrf_scores.get(doc_idx, 0.0) + (1.0 / (self.rrf_k + rank + 1))
            
        for rank, (doc_idx, _) in enumerate(dense_ranked):
            rrf_scores[doc_idx] = rrf_scores.get(doc_idx, 0.0) + (1.0 / (self.rrf_k + rank + 1))

        sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        results = []
        for doc_idx, score in sorted_rrf:
            results.append({
                "id": self.documents[doc_idx]["id"],
                "text": self.documents[doc_idx]["text"],
                "rrf_score": score,
                "metadata": self.documents[doc_idx]["metadata"]
            })
        return results

if __name__ == "__main__":
    engine = HybridRetrievalEngine()
    engine.ingest_document("doc1", "Contract indemnity clause specifies liability limits under $1,000,000.", [0.8, 0.1, 0.3])
    engine.ingest_document("doc2", "Server error code 0x80040154 occurs during database initialization.", [0.1, 0.9, 0.2])
    print(engine.search_hybrid("indemnity liability limits", [0.75, 0.15, 0.28], top_k=2))

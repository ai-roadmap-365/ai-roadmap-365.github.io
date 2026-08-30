import math
import re
from collections import Counter
from typing import List, Dict, Any, Tuple

class DocumentChunker:
    def __init__(self, chunk_size: int = 150, overlap: int = 30):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, doc_id: str, title: str, text: str) -> List[Dict[str, Any]]:
        words = text.split()
        chunks = []
        step = max(1, self.chunk_size - self.overlap)
        for i in range(0, len(words), step):
            chunk_words = words[i:i + self.chunk_size]
            if not chunk_words:
                break
            chunks.append({
                "chunk_id": f"{doc_id}#chunk_{len(chunks)}",
                "doc_id": doc_id,
                "title": title,
                "text": " ".join(chunk_words),
                "start_word": i,
                "end_word": i + len(chunk_words)
            })
            if i + self.chunk_size >= len(words):
                break
        return chunks

class SparseBM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: List[Dict[str, Any]] = []
        self.doc_freqs: List[Counter] = []
        self.doc_lengths: List[int] = []
        self.avg_dl: float = 0.0
        self.idf: Dict[str, float] = {}

    def index(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks
        self.doc_freqs = []
        self.doc_lengths = []
        df_counter = Counter()

        for chunk in chunks:
            tokens = re.findall(r'\w+', chunk["text"].lower())
            tf = Counter(tokens)
            self.doc_freqs.append(tf)
            self.doc_lengths.append(len(tokens))
            for term in tf.keys():
                df_counter[term] += 1

        n_docs = len(chunks)
        self.avg_dl = sum(self.doc_lengths) / max(1, n_docs)
        self.idf = {
            term: math.log((n_docs - freq + 0.5) / (freq + 0.5) + 1.0)
            for term, freq in df_counter.items()
        }

    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        q_tokens = re.findall(r'\w+', query.lower())
        scores = []

        for idx, tf in enumerate(self.doc_freqs):
            dl = self.doc_lengths[idx]
            score = 0.0
            for term in q_tokens:
                if term in tf:
                    term_idf = self.idf.get(term, 0.0)
                    freq = tf[term]
                    numerator = freq * (self.k1 + 1.0)
                    denominator = freq + self.k1 * (1.0 - self.b + self.b * (dl / max(1.0, self.avg_dl)))
                    score += term_idf * (numerator / denominator)
            scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

class HybridRanker:
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    def fuse_ranks(self, list_a: List[int], list_b: List[int]) -> List[Tuple[int, float]]:
        scores = Counter()
        for rank, doc_idx in enumerate(list_a, 1):
            scores[doc_idx] += 1.0 / (self.rrf_k + rank)
        for rank, doc_idx in enumerate(list_b, 1):
            scores[doc_idx] += 1.0 / (self.rrf_k + rank)
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

class PromptSynthesizer:
    @staticmethod
    def format_context(query: str, chunks: List[Dict[str, Any]]) -> str:
        blocks = []
        for i, c in enumerate(chunks, 1):
            blocks.append(f"[{i}] Title: {c['title']}\nContent: {c['text']}")
        joined = "\n\n".join(blocks)
        return (
            "You are a helpful technical assistant. Answer the user question using ONLY the provided context.\n"
            "Include inline bracketed citations matching document numbers, e.g. [1] or [2].\n\n"
            f"Context:\n{joined}\n\nQuestion: {query}\nAnswer:"
        )

if __name__ == "__main__":
    chunker = DocumentChunker(chunk_size=50, overlap=10)
    sample_text = (
        "Anthropic prompt caching allows developers to cache frequently used context. "
        "Cache writes cost $3.75 per million tokens for Claude 3.5 Sonnet, while cache reads cost $0.30 per million tokens. "
        "The minimum cacheable prompt length is 1024 tokens for Sonnet and Haiku models."
    )
    chunks = chunker.chunk_document("doc_01", "Claude Prompt Caching", sample_text)
    bm25 = SparseBM25()
    bm25.index(chunks)
    results = bm25.search("pricing prompt caching", top_k=1)
    prompt = PromptSynthesizer.format_context("What is prompt caching pricing?", [chunks[results[0][0]]])
    print(f"Ingested {len(chunks)} chunks.")
    print(f"Top Result Score: {results[0][1]:.4f}")
    print(f"Synthesized Prompt Length: {len(prompt)} characters.")

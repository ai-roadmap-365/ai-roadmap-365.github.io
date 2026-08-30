from typing import List, Dict, Any, Tuple

class DocumentChunker:
    def __init__(self, chunk_size: int = 150, overlap: int = 30):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, doc_id: str, title: str, text: str) -> List[Dict[str, Any]]:
        # Student implementation: split text into overlapping windows
        return []

class SparseBM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def index(self, chunks: List[Dict[str, Any]]):
        # Student implementation: compute token frequencies and IDFs
        pass

    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        # Student implementation: score candidate chunks
        return []

class HybridRanker:
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    def fuse_ranks(self, list_a: List[int], list_b: List[int]) -> List[Tuple[int, float]]:
        # Student implementation: reciprocal rank fusion
        return []

class PromptSynthesizer:
    @staticmethod
    def format_context(query: str, chunks: List[Dict[str, Any]]) -> str:
        # Student implementation: format prompt with numbered citations
        return ""

if __name__ == "__main__":
    print("Running starter scaffold...")

import hashlib
from typing import Dict, Any, List, Tuple

class HierarchicalChunker:
    def __init__(self, child_chunk_size_words: int = 15, parent_chunk_size_words: int = 60):
        self.child_size = int(child_chunk_size_words)
        self.parent_size = int(parent_chunk_size_words)
        self.parent_store: Dict[str, str] = {}
        self.child_index: List[Dict[str, Any]] = []
        
    def chunk_and_index_document(self, doc_id: str, full_text: str):
        words = full_text.split()
        if not words:
            return
            
        parent_idx = 0
        for p_start in range(0, len(words), self.parent_size):
            p_words = words[p_start : p_start + self.parent_size]
            p_text = " ".join(p_words)
            p_id = f"{doc_id}_p{parent_idx}"
            self.parent_store[p_id] = p_text
            parent_idx += 1
            
            child_idx = 0
            for c_start in range(0, len(p_words), self.child_size):
                c_words = p_words[c_start : c_start + self.child_size]
                c_text = " ".join(c_words)
                c_id = f"{p_id}_c{child_idx}"
                child_idx += 1
                
                self.child_index.append({
                    "child_id": c_id,
                    "parent_id": p_id,
                    "text": c_text,
                    "tokens": len(c_words)
                })

    def search_small_to_big(self, query: str, top_k_parents: int = 2) -> List[Dict[str, Any]]:
        q_words = set(query.lower().split())
        scored_children = []
        
        for child in self.child_index:
            c_words = set(child["text"].lower().split())
            overlap = len(q_words.intersection(c_words))
            scored_children.append((child, overlap))
            
        scored_children.sort(key=lambda x: x[1], reverse=True)
        
        matched_parents = {}
        for child, score in scored_children:
            if score == 0:
                continue
            p_id = child["parent_id"]
            if p_id not in matched_parents:
                matched_parents[p_id] = {
                    "parent_id": p_id,
                    "parent_text": self.parent_store[p_id],
                    "matched_child_id": child["child_id"],
                    "matched_child_text": child["text"],
                    "score": score
                }
            if len(matched_parents) >= top_k_parents:
                break
                
        return list(matched_parents.values())

if __name__ == "__main__":
    chunker = HierarchicalChunker(5, 15)
    chunker.chunk_and_index_document("d1", "Alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron")
    print(chunker.search_small_to_big("alpha beta"))

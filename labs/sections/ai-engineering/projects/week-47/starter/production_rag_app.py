import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple

class ProductionRAGApp:
    def __init__(self, confidence_threshold: float = 0.50):
        self.threshold = float(confidence_threshold)
        self.parent_store: Dict[str, Dict[str, Any]] = {}
        self.child_index: List[Dict[str, Any]] = []
        self.doc_metadata: Dict[str, Dict[str, Any]] = {}
        
    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def ingest_document(self, doc_id: str, title: str, section: str, text: str, child_size: int = 15) -> Dict[str, Any]:
        if not text or not text.strip():
            return {"status": "FAILED_EMPTY", "doc_id": doc_id}
            
        content_hash = self._hash(text)
        if doc_id in self.doc_metadata and self.doc_metadata[doc_id]["hash"] == content_hash:
            return {"status": "SKIPPED_UNCHANGED", "doc_id": doc_id}
            
        # Cascade delete old chunks if updating
        if doc_id in self.doc_metadata:
            self.child_index = [c for c in self.child_index if c["parent_id"] != doc_id]
            
        self.parent_store[doc_id] = {
            "doc_id": doc_id,
            "title": title,
            "section": section,
            "text": text
        }
        
        words = text.split()
        created_chunks = 0
        for i in range(0, len(words), child_size):
            c_text = " ".join(words[i : i + child_size])
            c_id = f"{doc_id}_c{created_chunks}"
            self.child_index.append({
                "child_id": c_id,
                "parent_id": doc_id,
                "text": c_text
            })
            created_chunks += 1
            
        self.doc_metadata[doc_id] = {
            "doc_id": doc_id,
            "hash": content_hash,
            "chunks_count": created_chunks
        }
        
        return {"status": "INDEXED_SUCCESS", "doc_id": doc_id, "chunks_created": created_chunks}

    def query(self, query_text: str) -> Dict[str, Any]:
        start_time = time.time()
        q_words = set(query_text.lower().split())
        
        if not self.child_index:
            return {
                "status": "REFUSED_EMPTY",
                "answer": "No documents in index.",
                "confidence": 0.0,
                "citations": []
            }
            
        scored_children = []
        for child in self.child_index:
            c_words = set(child["text"].lower().split())
            overlap = len(q_words.intersection(c_words))
            score = round(overlap / max(1, len(q_words)), 4)
            scored_children.append((child, score))
            
        scored_children.sort(key=lambda x: x[1], reverse=True)
        top_child, top_score = scored_children[0]
        
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        if top_score < self.threshold:
            return {
                "status": "REFUSED_LOW_CONFIDENCE",
                "answer": "I do not have sufficient verified documentation to answer this question.",
                "confidence": top_score,
                "citations": [],
                "telemetry": {"latency_ms": latency_ms, "candidates": len(scored_children)}
            }
            
        parent = self.parent_store[top_child["parent_id"]]
        marker = f"[{parent['doc_id']}: §{parent['section']}]"
        
        return {
            "status": "SUCCESS",
            "answer": f"According to verified documentation, {parent['text']} {marker}",
            "confidence": top_score,
            "citations": [
                {
                    "marker": marker,
                    "doc_id": parent["doc_id"],
                    "title": parent["title"],
                    "section": parent["section"]
                }
            ],
            "telemetry": {
                "latency_ms": latency_ms,
                "matched_parent": parent["doc_id"],
                "matched_child": top_child["child_id"]
            }
        }

if __name__ == "__main__":
    app = ProductionRAGApp(confidence_threshold=0.40)
    app.ingest_document("doc1", "SLA Policy", "4.1", "Enterprise tier uptime guarantee is 99.99 percent per calendar month")
    print(app.query("Enterprise uptime guarantee"))

import hashlib
from typing import Dict, Any, List, Optional

class ProductionIngestionPipeline:
    def __init__(self):
        self.metadata_store: Dict[str, Dict[str, Any]] = {}
        self.vector_index: Dict[str, Dict[str, Any]] = {}
        self.dead_letter_queue: List[Dict[str, Any]] = []
        
    def _compute_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def ingest_document(self, doc_id: str, text: str) -> Dict[str, Any]:
        if not text or not isinstance(text, str) or not text.strip():
            self.dead_letter_queue.append({"doc_id": doc_id, "error": "EMPTY_OR_INVALID_PAYLOAD"})
            return {"status": "FAILED_TO_DLQ", "doc_id": doc_id}
            
        new_hash = self._compute_hash(text)
        
        if doc_id in self.metadata_store:
            existing_hash = self.metadata_store[doc_id]["content_hash"]
            if existing_hash == new_hash:
                return {"status": "SKIPPED_UNCHANGED", "doc_id": doc_id, "hash": new_hash}
                
            old_chunks = self.metadata_store[doc_id]["chunk_ids"]
            for cid in old_chunks:
                self.vector_index.pop(cid, None)

        words = text.split()
        chunk_size = 20
        chunk_ids = []
        
        for i in range(0, len(words), chunk_size):
            c_text = " ".join(words[i : i + chunk_size])
            c_id = f"{doc_id}_c{len(chunk_ids)}"
            chunk_ids.append(c_id)
            
            self.vector_index[c_id] = {
                "chunk_id": c_id,
                "parent_id": doc_id,
                "text": c_text,
                "tokens": len(c_text.split())
            }
            
        self.metadata_store[doc_id] = {
            "doc_id": doc_id,
            "content_hash": new_hash,
            "chunk_ids": chunk_ids,
            "total_chunks": len(chunk_ids)
        }
        
        return {
            "status": "INDEXED_SUCCESS",
            "doc_id": doc_id,
            "chunks_created": len(chunk_ids),
            "hash": new_hash
        }

    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        if doc_id not in self.metadata_store:
            return {"status": "NOT_FOUND", "doc_id": doc_id}
            
        chunk_ids = self.metadata_store[doc_id]["chunk_ids"]
        for cid in chunk_ids:
            self.vector_index.pop(cid, None)
            
        del self.metadata_store[doc_id]
        return {"status": "DELETED_CASCADE_SUCCESS", "doc_id": doc_id, "deleted_chunks": len(chunk_ids)}

if __name__ == "__main__":
    p = ProductionIngestionPipeline()
    print(p.ingest_document("d1", "Alpha beta gamma delta epsilon"))
    print(p.ingest_document("d1", "Alpha beta gamma delta epsilon"))

import time
from typing import Dict, Any, List, Optional

class ProductionAssistantEngine:
    def __init__(self, confidence_threshold: float = 0.50):
        self.threshold = float(confidence_threshold)
        self.document_store: Dict[str, Dict[str, Any]] = {}
        
    def index_document(self, doc_id: str, title: str, section: str, text: str):
        self.document_store[doc_id] = {
            "doc_id": doc_id,
            "title": title,
            "section": section,
            "text": text
        }

    def process_query(self, query: str) -> Dict[str, Any]:
        start_time = time.time()
        q_words = set(query.lower().split())
        
        if not self.document_store:
            return {
                "status": "REFUSED_EMPTY_KNOWLEDGE_BASE",
                "answer": "No documents are indexed in the knowledge base.",
                "confidence_score": 0.0,
                "citations": [],
                "telemetry": {"latency_ms": 0.0, "candidates_evaluated": 0}
            }
            
        scored_candidates = []
        for doc_id, data in self.document_store.items():
            doc_words = set(data["text"].lower().split())
            overlap = len(q_words.intersection(doc_words))
            score = round(overlap / max(1, len(q_words)), 4)
            scored_candidates.append((data, score))
            
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        top_doc, top_score = scored_candidates[0]
        
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        if top_score < self.threshold:
            return {
                "status": "REFUSED_LOW_CONFIDENCE",
                "answer": "I do not have sufficient verified documentation in the knowledge base to answer this question accurately.",
                "confidence_score": top_score,
                "citations": [],
                "telemetry": {"latency_ms": latency_ms, "candidates_evaluated": len(scored_candidates)}
            }
            
        citation_id = f"[{top_doc['doc_id']}: §{top_doc['section']}]"
        generated_answer = f"Based on verified policy, {top_doc['text']} {citation_id}"
        
        return {
            "status": "SUCCESS",
            "answer": generated_answer,
            "confidence_score": top_score,
            "citations": [
                {
                    "marker": citation_id,
                    "doc_id": top_doc["doc_id"],
                    "title": top_doc["title"],
                    "section": top_doc["section"],
                    "text_snippet": top_doc["text"]
                }
            ],
            "telemetry": {
                "latency_ms": latency_ms,
                "candidates_evaluated": len(scored_candidates),
                "matched_doc_id": top_doc["doc_id"]
            }
        }

if __name__ == "__main__":
    ast = ProductionAssistantEngine()
    ast.index_document("d1", "Policy", "1.0", "Returns accepted in 30 days")
    print(ast.process_query("Returns accepted"))

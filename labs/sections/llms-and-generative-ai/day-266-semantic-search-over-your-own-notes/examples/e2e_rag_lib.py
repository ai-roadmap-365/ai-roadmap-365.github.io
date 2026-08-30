from typing import List, Dict, Any, Optional

class EndToEndRAGSystem:
    def __init__(self, confidence_threshold: float = 0.30):
        self.confidence_threshold = confidence_threshold
        self.documents: List[Dict[str, Any]] = []

    def ingest_corpus(self, docs: List[Dict[str, Any]]):
        self.documents = docs

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        q_words = set(query.lower().split())
        scored = []
        for doc in self.documents:
            d_words = set(doc["text"].lower().split())
            overlap = len(q_words.intersection(d_words))
            score = overlap / max(1, len(q_words))
            scored.append((doc, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [{"doc": doc, "score": score} for doc, score in scored[:top_k]]

    def synthesize_prompt(self, query: str, retrieved_items: List[Dict[str, Any]]) -> str:
        context_blocks = []
        for idx, item in enumerate(retrieved_items, 1):
            context_blocks.append(f"[{idx}] Source: {item['doc'].get('title', 'Doc')}\n{item['doc']['text']}")
        
        context_str = "\n\n".join(context_blocks)
        prompt = (
            "You are a helpful assistant. Answer the question STRICTLY using the context below. "
            "Cite sources using [1], [2]. If unknown, say you do not know.\n\n"
            f"Context:\n{context_str}\n\n"
            f"Question: {query}\n"
            "Answer:"
        )
        return prompt

    def query(self, user_query: str) -> Dict[str, Any]:
        retrieved = self.retrieve(user_query, top_k=3)
        if not retrieved or retrieved[0]["score"] < self.confidence_threshold:
            return {
                "answer": "I do not have sufficient documentation to answer this question accurately.",
                "citations": [],
                "retrieved_count": len(retrieved),
                "confidence": 0.0
            }

        prompt = self.synthesize_prompt(user_query, retrieved)
        top_doc = retrieved[0]["doc"]
        simulated_answer = f"According to documentation, {top_doc['text']} [1]."
        citations = [{"source_id": 1, "title": top_doc.get("title", "Doc")}]

        return {
            "answer": simulated_answer,
            "citations": citations,
            "retrieved_count": len(retrieved),
            "confidence": retrieved[0]["score"],
            "prompt_used": prompt
        }

def run_rag_demo():
    rag = EndToEndRAGSystem(confidence_threshold=0.30)
    docs = [
        {"title": "Auth Guide", "text": "API gateway tokens expire after 3600 seconds."},
        {"title": "Limits Guide", "text": "Standard accounts are rate limited to 500 RPM."}
    ]
    rag.ingest_corpus(docs)
    res_success = rag.query("API gateway tokens")
    res_fallback = rag.query("unrelated rocket science")

    print(f"Known Query Answer: {res_success['answer']}")
    print(f"Unknown Query Answer: {res_fallback['answer']}")
    return res_success, res_fallback

if __name__ == "__main__":
    run_rag_demo()

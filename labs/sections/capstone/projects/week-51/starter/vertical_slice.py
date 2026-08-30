import json
import time
from typing import Dict, Any, List

class AnswerPayload:
    def __init__(self, summary: str, detailed_points: List[str], citations: List[str], confidence_score: float):
        self.summary = summary
        self.detailed_points = detailed_points
        self.citations = citations
        self.confidence_score = float(confidence_score)

    def model_dump(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "detailed_points": self.detailed_points,
            "citations": self.citations,
            "confidence_score": self.confidence_score
        }

class CapstoneVerticalSlice:
    def __init__(self, model_fn=None):
        self.documents = [
            {"id": "doc1", "text": "Enterprise SLA guarantees 99.9% uptime with 24/7 dedicated support."},
            {"id": "doc2", "text": "Standard liability cap is fixed at $1,000,000 USD under Delaware governing law."}
        ]
        self.tools = {
            "calc_penalty": lambda base, rate: base * rate
        }
        self.model_fn = model_fn or self._default_model_fn

    def _default_model_fn(self, prompt: str) -> str:
        return json.dumps({
            "summary": "Enterprise SLA guarantees 99.9% uptime with a $1,000,000 liability cap.",
            "detailed_points": ["Uptime is 99.9% guaranteed", "Governing law is Delaware"],
            "citations": ["doc1", "doc2"],
            "confidence_score": 0.96
        })

    def hybrid_retrieval(self, query: str) -> List[Dict[str, Any]]:
        query_toks = set(query.lower().split())
        scored = []
        for doc in self.documents:
            doc_toks = set(doc["text"].lower().split())
            overlap = len(query_toks.intersection(doc_toks))
            scored.append((overlap, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored]

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        if tool_name in self.tools:
            return self.tools[tool_name](**kwargs)
        raise ValueError(f"Tool {tool_name} not found.")

    def run_query(self, user_query: str) -> Dict[str, Any]:
        t0 = time.perf_counter()
        
        # 1. Retrieval
        context_docs = self.hybrid_retrieval(user_query)
        context_str = "\n".join([f"<doc id='{d['id']}'>{d['text']}</doc>" for d in context_docs])
        
        # 2. Prompt Synthesis
        prompt = f"<context>\n{context_str}\n</context>\n<user_query>{user_query}</user_query>"
        
        # 3. Core AI Inference & Validation
        raw_resp = self.model_fn(prompt)
        data = json.loads(raw_resp)
        parsed_answer = AnswerPayload(**data)
        
        # 4. Tool Execution
        tool_result = self.execute_tool("calc_penalty", base=1000, rate=0.05)
        
        latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        
        return {
            "status": "SUCCESS",
            "latency_ms": latency_ms,
            "answer": parsed_answer.model_dump(),
            "retrieved_doc_count": len(context_docs),
            "tool_result": tool_result
        }

if __name__ == "__main__":
    slice_app = CapstoneVerticalSlice()
    print(json.dumps(slice_app.run_query("What is SLA?"), indent=2))

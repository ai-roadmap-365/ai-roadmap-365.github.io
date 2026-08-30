import json
import time
from typing import Dict, Any, List, Tuple

class AnswerPayload:
    def __init__(self, summary: str, detailed_points: List[str], citations: List[str], confidence_score: float):
        self.summary = summary
        self.detailed_points = detailed_points
        self.citations = citations
        self.confidence_score = float(confidence_score)
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("confidence_score must be between 0 and 1")
        if not isinstance(self.detailed_points, list):
            raise TypeError("detailed_points must be a list")

    def model_dump(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "detailed_points": self.detailed_points,
            "citations": self.citations,
            "confidence_score": self.confidence_score
        }

class CoreAIEngine:
    def __init__(self, primary_model_fn, fallback_model_fn=None, failure_threshold: int = 3, timeout_seconds: float = 2.5):
        self.primary_model_fn = primary_model_fn
        self.fallback_model_fn = fallback_model_fn
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.consecutive_failures = 0
        self.circuit_open = False

    def synthesize_prompt(self, user_query: str, context_chunks: List[Dict[str, Any]]) -> str:
        context_str = "\n".join([f"<doc id='{c.get('id', 'N/A')}'>{c.get('text', '')}</doc>" for c in context_chunks])
        return (
            "<system_instruction>\n"
            "You are a factual enterprise AI assistant. Answer using strictly the provided context.\n"
            "Output your answer strictly in valid JSON conforming to the AnswerPayload schema.\n"
            "</system_instruction>\n\n"
            f"<context>\n{context_str}\n</context>\n\n"
            f"<user_query>\n{user_query}\n</user_query>"
        )

    def execute_inference_with_fallback(self, prompt: str) -> Tuple[str, str]:
        if not self.circuit_open:
            try:
                start = time.perf_counter()
                resp = self.primary_model_fn(prompt)
                if time.perf_counter() - start > self.timeout_seconds:
                    raise TimeoutError("Primary LLM exceeded latency budget.")
                self.consecutive_failures = 0
                return resp, "primary_model"
            except Exception:
                self.consecutive_failures += 1
                if self.consecutive_failures >= self.failure_threshold:
                    self.circuit_open = True

        if self.fallback_model_fn:
            resp = self.fallback_model_fn(prompt)
            return resp, "fallback_model"
        raise RuntimeError("Primary model failed and no fallback available.")

    def parse_and_repair_json(self, raw_text: str, max_retries: int = 1) -> AnswerPayload:
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
            return AnswerPayload(**data)
        except Exception as err:
            if max_retries > 0:
                repair_prompt = f"Fix this invalid JSON to match the AnswerPayload schema. Errors: {err}\nInvalid JSON:\n{cleaned}"
                fixed_raw, _ = self.execute_inference_with_fallback(repair_prompt)
                return self.parse_and_repair_json(fixed_raw, max_retries=max_retries - 1)
            raise ValueError(f"Failed to parse structured JSON output: {err}")

if __name__ == "__main__":
    def mock_primary(p: str) -> str:
        return '{"summary": "SLA is 99.9%.", "detailed_points": ["Point 1"], "citations": ["doc1"], "confidence_score": 0.95}'
    engine = CoreAIEngine(primary_model_fn=mock_primary)
    prompt = engine.synthesize_prompt("What is SLA?", [{"id": "doc1", "text": "SLA is 99.9%."}])
    raw, prov = engine.execute_inference_with_fallback(prompt)
    print("Parsed:", engine.parse_and_repair_json(raw).summary)

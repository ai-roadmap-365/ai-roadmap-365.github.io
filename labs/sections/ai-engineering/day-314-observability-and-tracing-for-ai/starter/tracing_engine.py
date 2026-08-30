import time
import uuid
import json
from typing import Dict, Any, List, Optional

class Span:
    def __init__(self, name: str, kind: str, parent_id: Optional[str] = None):
        self.span_id = str(uuid.uuid4())[:8]
        self.parent_id = parent_id
        self.name = name
        self.kind = kind
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.duration_ms: float = 0.0
        self.attributes: Dict[str, Any] = {}
        self.children: List['Span'] = []
        
    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value
        
    def finish(self):
        self.end_time = time.time()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "kind": self.kind,
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
            "children": [c.to_dict() for c in self.children]
        }

class TraceTelemetryEngine:
    def __init__(self):
        self.traces: Dict[str, Span] = {}
        
    def start_trace(self, name: str) -> Span:
        root_span = Span(name=name, kind="ROOT")
        self.traces[root_span.span_id] = root_span
        return root_span
        
    def create_child_span(self, parent_span: Span, name: str, kind: str) -> Span:
        child = Span(name=name, kind=kind, parent_id=parent_span.span_id)
        parent_span.children.append(child)
        return child
        
    @staticmethod
    def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str = "claude-3-5-sonnet") -> float:
        cost = (prompt_tokens * 3.0 / 1_000_000) + (completion_tokens * 15.0 / 1_000_000)
        return round(cost, 6)

if __name__ == "__main__":
    engine = TraceTelemetryEngine()
    root = engine.start_trace("Test_Trace")
    root.finish()
    print("Trace Root:", root.to_dict())

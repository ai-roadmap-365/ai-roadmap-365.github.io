import re
from typing import List, Dict, Any

class RAGTriadEvaluator:
    def __init__(self):
        pass

    def evaluate_faithfulness(self, context: str, answer: str) -> Dict[str, Any]:
        # TODO: Split answer into claims and verify grounding against context
        pass

    def evaluate_context_relevance(self, query: str, context: str) -> float:
        # TODO: Calculate fraction of context sentences relevant to query
        pass

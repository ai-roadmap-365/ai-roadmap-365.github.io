from typing import List, Dict, Any
from collections import Counter

class FewShotCoTEngine:
    def __init__(self, task_description: str):
        self.task_description = task_description
        self.exemplars: List[Dict[str, str]] = []

    def add_exemplar(self, question: str, reasoning: str, answer: str) -> "FewShotCoTEngine":
        # TODO: Add exemplar
        pass

    def compile_prompt(self, query: str) -> str:
        # TODO: Compile XML CoT prompt
        pass

    @staticmethod
    def aggregate_self_consistency(sampled_answers: List[str]) -> Dict[str, Any]:
        # TODO: Perform majority voting
        pass

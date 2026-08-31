"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import json
from typing import List, Dict, Any, Tuple

class CapstoneEvaluationEngine:

    def __init__(self, faithfulness_threshold: float=0.9, recall_threshold: float=0.85):
        self.faithfulness_threshold = faithfulness_threshold
        self.recall_threshold = recall_threshold

    def calculate_faithfulness(self, answer_claims: List[str], context_text: str) -> Tuple[float, List[str]]:
        raise NotImplementedError('TASK 1: implement calculate_faithfulness.')

    def calculate_context_recall(self, ground_truth_points: List[str], context_text: str) -> float:
        raise NotImplementedError('TASK 2: implement calculate_context_recall.')

    def evaluate_benchmark_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError('TASK 3: implement evaluate_benchmark_item.')

    def run_eval_suite(self, benchmark_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        raise NotImplementedError('TASK 4: implement run_eval_suite.')
if __name__ == '__main__':
    benchmark = [{'id': 'q1', 'ground_truth_points': ['Uptime is 99.9%'], 'retrieved_context': 'The system uptime is 99.9% guaranteed.', 'answer_claims': ['Uptime is 99.9%']}]
    engine = CapstoneEvaluationEngine()
    print(engine.run_eval_suite(benchmark))

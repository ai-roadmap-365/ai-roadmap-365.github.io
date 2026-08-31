"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import json
import re
import uuid
import time
from typing import Dict, Any, List, Optional, Tuple

class EvaluationHarnessSuite:

    def __init__(self, baseline_score: float=0.85, tolerance_delta: float=-0.02):
        self.baseline_score = float(baseline_score)
        self.tolerance_delta = float(tolerance_delta)
        self.dataset: List[Dict[str, Any]] = []
        self.results: List[Dict[str, Any]] = []

    def add_benchmark_case(self, case_id: str, category: str, query: str, ground_truth: str, is_golden: bool=False) -> bool:
        raise NotImplementedError('TASK 1: implement add_benchmark_case.')

    @staticmethod
    def evaluate_exact_match(pred: str, gt: str) -> float:
        raise NotImplementedError('TASK 2: implement evaluate_exact_match.')

    @staticmethod
    def evaluate_token_f1(pred: str, gt: str) -> float:
        raise NotImplementedError('TASK 3: implement evaluate_token_f1.')

    @staticmethod
    def evaluate_json_f1(pred_json_str: str, gt_dict: Dict[str, Any]) -> float:
        raise NotImplementedError('TASK 4: implement evaluate_json_f1.')

    def run_benchmark_case(self, case_id: str, candidate_prediction: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError('TASK 5: implement run_benchmark_case.')

    def evaluate_suite_regression(self) -> Dict[str, Any]:
        raise NotImplementedError('TASK 6: implement evaluate_suite_regression.')
if __name__ == '__main__':
    suite = EvaluationHarnessSuite(baseline_score=0.8)
    suite.add_benchmark_case('c1', 'happy_path', 'What is Paris?', 'Paris is the capital of France.', is_golden=True)
    suite.run_benchmark_case('c1', 'Paris is the capital of France.')
    print('Suite Decision:', suite.evaluate_suite_regression())

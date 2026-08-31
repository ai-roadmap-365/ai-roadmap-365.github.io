"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import json
from typing import List, Dict, Any, Optional

class CompleteEvalHarness:

    def __init__(self, baseline_composite_score: float=0.85, tolerance_delta: float=-0.02):
        self.baseline_score = float(baseline_composite_score)
        self.tolerance_delta = float(tolerance_delta)
        self.results: List[Dict[str, Any]] = []

    def evaluate_case(self, case_id: str, category: str, prediction: str, ground_truth: str, is_golden: bool=False) -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement evaluate_case.')

    def generate_report(self) -> Dict[str, Any]:
        raise NotImplementedError('TASK 2: implement generate_report.')
if __name__ == '__main__':
    harness = CompleteEvalHarness(baseline_composite_score=0.8)
    harness.evaluate_case('c1', 'happy_path', 'Paris', 'Paris', is_golden=True)
    print('Report:', harness.generate_report())

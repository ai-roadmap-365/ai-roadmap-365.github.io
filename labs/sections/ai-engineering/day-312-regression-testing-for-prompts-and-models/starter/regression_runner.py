"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

from typing import Dict, Any, List

class RegressionTestRunner:

    def __init__(self, tolerance_delta: float=-0.02):
        self.tolerance_delta = tolerance_delta

    def evaluate_regression(self, baseline_results: Dict[str, Any], candidate_results: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement evaluate_regression.')
if __name__ == '__main__':
    runner = RegressionTestRunner(tolerance_delta=-0.02)
    base = {'accuracy': 0.9, 'schema_validity': 1.0, 'failed_golden_cases': []}
    cand = {'accuracy': 0.92, 'schema_validity': 1.0, 'failed_golden_cases': []}
    print('Report:', runner.evaluate_regression(base, cand))

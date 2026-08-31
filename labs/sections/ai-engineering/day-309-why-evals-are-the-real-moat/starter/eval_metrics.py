"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import json
import re
from typing import Dict, Any

class EvalMetricEngine:

    @staticmethod
    def exact_match(prediction: str, ground_truth: str) -> float:
        raise NotImplementedError('TASK 1: implement exact_match.')

    @staticmethod
    def json_field_f1(predicted_json_str: str, ground_truth_dict: Dict[str, Any]) -> Dict[str, float]:
        raise NotImplementedError('TASK 2: implement json_field_f1.')

    @staticmethod
    def token_overlap_f1(prediction: str, ground_truth: str) -> float:
        raise NotImplementedError('TASK 3: implement token_overlap_f1.')
if __name__ == '__main__':
    engine = EvalMetricEngine()
    print('Exact Match:', engine.exact_match('Paris', 'paris'))

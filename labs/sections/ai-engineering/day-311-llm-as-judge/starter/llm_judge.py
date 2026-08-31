"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import json
import re
from typing import Dict, Any

class LLMJudgeEvaluator:

    @staticmethod
    def build_rubric_prompt(query: str, context: str, candidate_answer: str) -> str:
        raise NotImplementedError('TASK 1: implement build_rubric_prompt.')

    @staticmethod
    def parse_judge_response(raw_response: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 2: implement parse_judge_response.')

    @staticmethod
    def resolve_pairwise_swap(pass1_winner: str, pass2_winner: str) -> str:
        raise NotImplementedError('TASK 3: implement resolve_pairwise_swap.')
if __name__ == '__main__':
    judge = LLMJudgeEvaluator()
    sample_json = '```json\n{"reasoning": "Fully grounded in doc 1", "score": 5}\n```'
    print('Parsed Judge Output:', judge.parse_judge_response(sample_json))

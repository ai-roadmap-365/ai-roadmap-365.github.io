"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import json
import os
from typing import List, Dict, Any, Optional

class EvalDatasetCurator:

    def __init__(self):
        self.records: List[Dict[str, Any]] = []

    def add_record(self, record_id: str, category: str, query: str, expected_output: str, metadata: Optional[Dict[str, Any]]=None) -> bool:
        raise NotImplementedError('TASK 1: implement add_record.')

    def get_stratified_counts(self) -> Dict[str, int]:
        raise NotImplementedError('TASK 2: implement get_stratified_counts.')

    def export_jsonl(self, filepath: str) -> int:
        raise NotImplementedError('TASK 3: implement export_jsonl.')

    def load_jsonl(self, filepath: str) -> int:
        raise NotImplementedError('TASK 4: implement load_jsonl.')
if __name__ == '__main__':
    curator = EvalDatasetCurator()
    curator.add_record('eval_01', 'happy_path', 'What is the return policy?', '30 days with receipt.')
    print('Stratified counts:', curator.get_stratified_counts())

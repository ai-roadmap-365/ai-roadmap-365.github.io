"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import subprocess
import os
from typing import Dict, Any, List

class FeatureOrchestrator:

    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.realpath(workspace_root)

    def execute_quality_gates(self, test_cmd: str='python3 -m unittest') -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement execute_quality_gates.')

    def generate_walkthrough_artifact(self, feature_name: str, files_modified: List[str], test_results: Dict[str, Any]) -> str:
        raise NotImplementedError('TASK 2: implement generate_walkthrough_artifact.')
if __name__ == '__main__':
    orchestrator = FeatureOrchestrator('.')
    res = orchestrator.execute_quality_gates('python3 -c \'print("Tests OK")\'')
    print(orchestrator.generate_walkthrough_artifact('Demo Feature', ['a.py'], res)[:200])

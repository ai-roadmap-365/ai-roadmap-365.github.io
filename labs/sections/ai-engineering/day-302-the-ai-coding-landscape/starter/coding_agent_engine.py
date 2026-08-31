"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import os
import subprocess
from typing import Dict, Any, List

class CodingAgentEngine:

    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.realpath(workspace_root)

    def generate_repo_map(self) -> str:
        raise NotImplementedError('TASK 1: implement generate_repo_map.')

    def apply_search_replace(self, file_rel_path: str, search_block: str, replace_block: str) -> str:
        raise NotImplementedError('TASK 2: implement apply_search_replace.')

    def run_verification_tests(self, test_command: str='python3 -m unittest discover') -> Dict[str, Any]:
        raise NotImplementedError('TASK 3: implement run_verification_tests.')
if __name__ == '__main__':
    engine = CodingAgentEngine('.')
    print('Repo map preview:\n', engine.generate_repo_map())

"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import subprocess
import os
from typing import Dict, Any, List

class HeadlessCIAgentRunner:

    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.realpath(workspace_root)

    def execute_test_command(self, cmd: str='python3 -m unittest') -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement execute_test_command.')

    def generate_pr_summary(self, issue_id: str, title: str, changes: List[str]) -> str:
        raise NotImplementedError('TASK 2: implement generate_pr_summary.')
if __name__ == '__main__':
    runner = HeadlessCIAgentRunner('.')
    print(runner.generate_pr_summary('1', 'Fix bug', ['Fix line 1']))

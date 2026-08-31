"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import subprocess
import re
from typing import Dict, Any

class SelfHealingTestRunner:

    def __init__(self, workspace_root: str, max_iterations: int=4):
        self.workspace_root = workspace_root
        self.max_iterations = max_iterations

    def execute_test_command(self, test_cmd: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement execute_test_command.')

    def extract_traceback_diagnostics(self, raw_output: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 2: implement extract_traceback_diagnostics.')

    def format_repair_prompt(self, diagnostics: Dict[str, Any], raw_output: str) -> str:
        raise NotImplementedError('TASK 3: implement format_repair_prompt.')
if __name__ == '__main__':
    runner = SelfHealingTestRunner('.')
    res = runner.execute_test_command('python3 -c \'print("Tests OK")\'')
    print('Execution output:', res['stdout'].strip())

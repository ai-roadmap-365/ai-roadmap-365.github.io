"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import os
from typing import List

class SpecCompiler:

    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.realpath(workspace_root)

    def bundle_context(self, relative_file_paths: List[str]) -> str:
        raise NotImplementedError('TASK 1: implement bundle_context.')

    def compile_prompt(self, goal: str, target_files: List[str], constraints: List[str], non_goals: List[str], verification_command: str) -> str:
        raise NotImplementedError('TASK 2: implement compile_prompt.')
if __name__ == '__main__':
    compiler = SpecCompiler('.')
    res = compiler.compile_prompt('Refactor API', ['app.py'], ['Speed up'], ['Do not break tests'], 'pytest')
    print(res[:200])

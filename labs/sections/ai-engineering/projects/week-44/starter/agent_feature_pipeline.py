"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import os
import ast
import subprocess
import re
from typing import Dict, Any, List, Optional

class AgentFeaturePipeline:

    def __init__(self, workspace_root: str, approved_packages: Optional[List[str]]=None):
        self.workspace_root = os.path.realpath(workspace_root)
        self.approved_packages = set(approved_packages or ['os', 'sys', 'math', 'pytest', 'typing'])

    def generate_repo_map(self) -> str:
        raise NotImplementedError('TASK 1: implement generate_repo_map.')

    def apply_patch(self, file_rel_path: str, search_block: str, replace_block: str) -> str:
        raise NotImplementedError('TASK 2: implement apply_patch.')

    def audit_security(self, source_code: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 3: implement audit_security.')

    def run_tests(self, test_cmd: str='python3 -m unittest') -> Dict[str, Any]:
        raise NotImplementedError('TASK 4: implement run_tests.')

    def format_walkthrough(self, feature_name: str, modified_files: List[str], test_res: Dict[str, Any]) -> str:
        raise NotImplementedError('TASK 5: implement format_walkthrough.')
if __name__ == '__main__':
    pipeline = AgentFeaturePipeline('.')
    print('Pipeline ready. Workspace map preview:\n', pipeline.generate_repo_map()[:100])

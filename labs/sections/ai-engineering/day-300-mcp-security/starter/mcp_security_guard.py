"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import os
from typing import Dict, Any, Callable, List

class MCPSecurityGuard:

    def __init__(self, sandbox_root: str):
        self.sandbox_root = os.path.realpath(sandbox_root)
        self.destructive_tools = {'delete_file', 'drop_table', 'execute_shell'}
        self.audit_log: List[Dict[str, Any]] = []

    def validate_path(self, relative_path: str) -> str:
        raise NotImplementedError('TASK 1: implement validate_path.')

    def authorize_and_execute(self, tool_name: str, arguments: Dict[str, Any], handler_fn: Callable, human_approved: bool=False) -> Dict[str, Any]:
        raise NotImplementedError('TASK 2: implement authorize_and_execute.')
if __name__ == '__main__':
    guard = MCPSecurityGuard('/tmp/mcp_sandbox')
    print('Sandbox root:', guard.sandbox_root)
    res = guard.authorize_and_execute('read_file', {'path': 'safe.txt'}, lambda a: 'File data')
    print('Safe read result:', res)

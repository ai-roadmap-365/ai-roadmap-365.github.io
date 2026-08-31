"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import sqlite3
from typing import Dict, Any, List

class PersonalMCPServer:

    def __init__(self, db_path: str=':memory:'):
        raise NotImplementedError('TASK 1: implement __init__.')

    def _init_db(self):
        raise NotImplementedError('TASK 2: implement _init_db.')

    def save_memo(self, title: str, content: str, tags: str='') -> str:
        raise NotImplementedError('TASK 3: implement save_memo.')

    def search_memos(self, keyword: str) -> List[Dict[str, Any]]:
        raise NotImplementedError('TASK 4: implement search_memos.')

    def add_todo(self, task: str) -> str:
        raise NotImplementedError('TASK 5: implement add_todo.')

    def get_pending_todos_resource(self) -> str:
        raise NotImplementedError('TASK 6: implement get_pending_todos_resource.')

    def generate_standup_prompt(self, recent_commits: str) -> List[Dict[str, Any]]:
        raise NotImplementedError('TASK 7: implement generate_standup_prompt.')
if __name__ == '__main__':
    server = PersonalMCPServer(':memory:')
    print(server.save_memo('Test Memo', 'Discussing MCP architecture', 'mcp,architecture'))
    print(server.add_todo('Write test suite for personal server'))
    print('Search:', server.search_memos('architecture'))
    print('Resource:', server.get_pending_todos_resource())
    print('Prompt:', server.generate_standup_prompt('feat: initial commit'))

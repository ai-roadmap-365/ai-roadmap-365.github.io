"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import sqlite3
import json
import os
from typing import Dict, Any, List, Optional

class PersonalMCPDaemon:

    def __init__(self, db_path: str=':memory:', sandbox_root: str='/tmp'):
        raise NotImplementedError('TASK 1: implement __init__.')

    def _init_db(self):
        raise NotImplementedError('TASK 2: implement _init_db.')

    def validate_path(self, relative_path: str) -> str:
        raise NotImplementedError('TASK 3: implement validate_path.')

    def handle_request(self, request_str: str) -> str:
        raise NotImplementedError('TASK 4: implement handle_request.')
if __name__ == '__main__':
    daemon = PersonalMCPDaemon(':memory:')
    res = daemon.handle_request('{"jsonrpc": "2.0", "id": 1, "method": "initialize"}')
    print('Init response:', res)

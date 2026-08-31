"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import json
import os
import sys
from typing import Dict, Any, List, Optional

class MCPConfigParser:

    @staticmethod
    def parse_config(config_json: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement parse_config.')

class MockMCPServerProcess:
    """In-memory mock representing a subprocess stdio pipe for testing."""

    def __init__(self, name: str='mock-server'):
        self.name = name
        self.tools = {'get_status': lambda args: {'status': 'ONLINE', 'uptime_sec': 4200}}

    def process_line(self, line: str) -> Optional[str]:
        raise NotImplementedError('TASK 2: implement process_line.')

class LocalMCPRunner:

    def __init__(self, server_name: str, config: Dict[str, Any]):
        self.server_name = server_name
        self.config = config
        self.mock_proc = MockMCPServerProcess(server_name)
        self.request_id = 0

    def initialize(self) -> Dict[str, Any]:
        raise NotImplementedError('TASK 3: implement initialize.')

    def list_tools(self) -> List[Dict[str, Any]]:
        raise NotImplementedError('TASK 4: implement list_tools.')

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError('TASK 5: implement call_tool.')
if __name__ == '__main__':
    runner = LocalMCPRunner('test-srv', {'command': 'python', 'args': []})
    init_res = runner.initialize()
    print('Initialized:', init_res['result']['serverInfo'])
    tools = runner.list_tools()
    print('Tools:', tools)
    call_res = runner.call_tool('get_status', {})
    print('Call result:', call_res['content'][0]['text'])

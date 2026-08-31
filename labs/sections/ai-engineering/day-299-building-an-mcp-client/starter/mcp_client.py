"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import json
from typing import Dict, Any, List, Optional

class MockMCPServerInstance:

    def __init__(self, name: str, tools_dict: Dict[str, Any]):
        self.name = name
        self.tools_dict = tools_dict

    def handle_line(self, line: str) -> Optional[str]:
        raise NotImplementedError('TASK 1: implement handle_line.')

class AutonomousMCPAgent:

    def __init__(self):
        self.servers: Dict[str, MockMCPServerInstance] = {}
        self.tool_routing: Dict[str, MockMCPServerInstance] = {}
        self.unified_tools: List[Dict[str, Any]] = []
        self.req_id = 0

    def register_server(self, name: str, server_instance: MockMCPServerInstance):
        raise NotImplementedError('TASK 2: implement register_server.')

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        raise NotImplementedError('TASK 3: implement execute_tool.')
if __name__ == '__main__':
    agent = AutonomousMCPAgent()
    srv1 = MockMCPServerInstance('db-srv', {'query_users': lambda args: 'Alice, Bob'})
    srv2 = MockMCPServerInstance('fs-srv', {'read_file': lambda args: 'File contents: OK'})
    agent.register_server('db-srv', srv1)
    agent.register_server('fs-srv', srv2)
    print('Unified tools:', [t['name'] for t in agent.unified_tools])
    print('DB Result:', agent.execute_tool('query_users', {}))
    print('FS Result:', agent.execute_tool('read_file', {}))

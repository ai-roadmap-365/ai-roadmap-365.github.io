"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import json
from typing import Dict, Any, Optional

class MCPProtocolHandler:

    def __init__(self, server_name: str='demo-server', server_version: str='1.0.0'):
        self.server_name = server_name
        self.server_version = server_version
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: str, description: str, input_schema: Dict[str, Any], handler_fn):
        raise NotImplementedError('TASK 1: implement register_tool.')

    def handle_message(self, raw_message: str) -> Optional[str]:
        raise NotImplementedError('TASK 2: implement handle_message.')
if __name__ == '__main__':
    server = MCPProtocolHandler('math-server', '1.0.0')
    server.register_tool('add', 'Add two numbers', {'type': 'object', 'properties': {'a': {'type': 'number'}, 'b': {'type': 'number'}}}, lambda args: args['a'] + args['b'])
    resp = server.handle_message('{"jsonrpc": "2.0", "id": 1, "method": "initialize"}')
    print('Init response:', resp)

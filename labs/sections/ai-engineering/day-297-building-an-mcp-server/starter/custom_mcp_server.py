"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import inspect
import json
from typing import Dict, Any, Callable, get_type_hints, List, Optional

class CustomMCPServer:

    def __init__(self, name: str='custom-mcp-server'):
        self.name = name
        self.tools: Dict[str, Dict[str, Any]] = {}

    def tool(self, name: Optional[str]=None, description: Optional[str]=None):
        raise NotImplementedError('TASK 2: implement tool.')

    def list_tools(self) -> List[Dict[str, Any]]:
        raise NotImplementedError('TASK 3: implement list_tools.')

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError('TASK 4: implement call_tool.')
if __name__ == '__main__':
    server = CustomMCPServer('retail-tools')

    @server.tool()
    def calculate_tax(amount: float, rate: float=0.08) -> float:
        """Calculate total amount including tax."""
        raise NotImplementedError('TASK 5: implement calculate_tax. Calculate total amount including tax.')
    print('Registered tools:', server.list_tools())
    res = server.call_tool('calculate_tax', {'amount': 100.0, 'rate': 0.1})
    print('Execution result:', res)

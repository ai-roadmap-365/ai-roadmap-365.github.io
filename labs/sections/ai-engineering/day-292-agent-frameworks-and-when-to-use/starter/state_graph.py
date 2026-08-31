"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

from typing import Dict, Any, Callable, List, Optional, Tuple

class StateGraphEngine:

    def __init__(self):
        self.nodes: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, Tuple[Callable[[Dict[str, Any]], str], Dict[str, str]]] = {}
        self.entry_point: Optional[str] = None
        self.checkpoints: List[Dict[str, Any]] = []

    def add_node(self, name: str, func: Callable[[Dict[str, Any]], Dict[str, Any]]):
        raise NotImplementedError('TASK 1: implement add_node.')

    def set_entry_point(self, name: str):
        raise NotImplementedError('TASK 2: implement set_entry_point.')

    def add_edge(self, start_node: str, end_node: str):
        raise NotImplementedError('TASK 3: implement add_edge.')

    def add_conditional_edges(self, source_node: str, router_fn: Callable[[Dict[str, Any]], str], route_map: Dict[str, str]):
        raise NotImplementedError('TASK 4: implement add_conditional_edges.')

    def run(self, initial_state: Dict[str, Any], max_steps: int=10) -> Dict[str, Any]:
        raise NotImplementedError('TASK 5: implement run.')

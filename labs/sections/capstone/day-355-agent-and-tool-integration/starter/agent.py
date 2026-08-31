"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import json
from typing import Dict, Any, List, Callable, Tuple

class ToolDefinition:

    def __init__(self, name: str, description: str, parameters_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters_schema = parameters_schema

class AgentCheckpoint:

    def __init__(self, turn: int, thought: str, action: str, action_input: Dict[str, Any], observation: str):
        self.turn = turn
        self.thought = thought
        self.action = action
        self.action_input = action_input
        self.observation = observation

    def model_dump(self) -> Dict[str, Any]:
        raise NotImplementedError('TASK 1: implement model_dump.')

class AgentOrchestrator:

    def __init__(self, model_fn: Callable[[str], str], max_turns: int=5):
        self.model_fn = model_fn
        self.max_turns = max_turns
        self.tool_registry: Dict[str, Tuple[ToolDefinition, Callable]] = {}
        self.checkpoints: List[AgentCheckpoint] = []

    def register_tool(self, name: str, description: str, param_schema: Dict[str, Any], handler: Callable):
        raise NotImplementedError('TASK 2: implement register_tool.')

    def _execute_sandboxed_tool(self, name: str, args: Dict[str, Any]) -> str:
        raise NotImplementedError('TASK 3: implement _execute_sandboxed_tool.')

    def run_agent(self, user_goal: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 4: implement run_agent.')
if __name__ == '__main__':

    def mock_db(account_id: str):
        raise NotImplementedError('TASK 5: implement mock_db.')
    agent = AgentOrchestrator(model_fn=lambda p: '{"thought": "done", "action": "FINAL_ANSWER", "action_input": {"answer": "15000"}}')
    agent.register_tool('get_balance', 'Get account balance', {}, mock_db)
    print(agent.run_agent('Check balance'))

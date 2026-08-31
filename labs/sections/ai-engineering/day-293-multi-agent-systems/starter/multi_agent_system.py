"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

from typing import Dict, Any, List, Optional
import time

class AgentMessage:

    def __init__(self, sender: str, recipient: str, content: str, msg_type: str):
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.msg_type = msg_type
        self.timestamp = time.time()

class MessageBus:

    def __init__(self):
        self.history: List[AgentMessage] = []

    def send(self, msg: AgentMessage):
        raise NotImplementedError('TASK 1: implement send.')

    def get_messages_for(self, recipient: str) -> List[AgentMessage]:
        raise NotImplementedError('TASK 2: implement get_messages_for.')

class MultiAgentSupervisorSystem:

    def __init__(self, max_rounds: int=5):
        self.bus = MessageBus()
        self.max_rounds = max_rounds

    def _researcher_turn(self, task: str) -> str:
        raise NotImplementedError('TASK 3: implement _researcher_turn.')

    def _critic_turn(self, draft: str) -> str:
        raise NotImplementedError('TASK 4: implement _critic_turn.')

    def _supervisor_turn(self, goal: str, round_num: int) -> Dict[str, Any]:
        raise NotImplementedError('TASK 5: implement _supervisor_turn.')

    def run(self, goal: str) -> Dict[str, Any]:
        raise NotImplementedError('TASK 6: implement run.')

import time
from typing import Dict, Any, List, Optional
from collections import deque

class CLIAssistantCore:
    def __init__(self, system_prompt: str, max_history_turns: int = 6):
        # TODO: Initialize attributes and sliding history deque
        pass

    def register_tool(self, name: str, func: Any):
        # TODO: Register tool
        pass

    def build_message_context(self, new_user_message: str) -> List[Dict[str, Any]]:
        # TODO: Construct message context with system prompt and history
        pass

    def record_turn(self, user_text: str, assistant_text: str, tokens: int = 150, cost: float = 0.0005):
        # TODO: Record turn and update ledger
        pass

    def handle_slash_command(self, cmd: str) -> str:
        # TODO: Process slash commands (/help, /cost, /clear, /tools)
        pass

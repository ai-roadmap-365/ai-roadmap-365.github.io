import time
from typing import Dict, Any, List, Optional
from collections import deque

class CLIAssistantCore:
    def __init__(self, system_prompt: str, max_history_turns: int = 6):
        self.system_prompt = system_prompt
        self.max_history_turns = max_history_turns
        self.history: deque = deque(maxlen=max_history_turns * 2)
        self.tools: Dict[str, Any] = {}
        self.session_cost_usd = 0.0
        self.total_tokens_consumed = 0

    def register_tool(self, name: str, func: Any):
        self.tools[name] = func

    def build_message_context(self, new_user_message: str) -> List[Dict[str, Any]]:
        messages = [{"role": "system", "content": self.system_prompt}]
        for turn in self.history:
            messages.append(turn)
        messages.append({"role": "user", "content": new_user_message})
        return messages

    def record_turn(self, user_text: str, assistant_text: str, tokens: int = 150, cost: float = 0.0005):
        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": assistant_text})
        self.total_tokens_consumed += tokens
        self.session_cost_usd += cost

    def handle_slash_command(self, cmd: str) -> str:
        cmd = cmd.strip().lower()
        if cmd == "/help":
            return "Available commands: /help, /cost, /clear, /tools, /exit"
        elif cmd == "/cost":
            return f"Session Tokens: {self.total_tokens_consumed} | Total Cost: ${self.session_cost_usd:.4f}"
        elif cmd == "/clear":
            self.history.clear()
            return "Conversation history cleared. System prompt preserved."
        elif cmd == "/tools":
            return f"Registered Tools: {list(self.tools.keys())}"
        return f"Unknown command: {cmd}"

def run_assistant_demo():
    assistant = CLIAssistantCore("You are a helpful assistant.", max_history_turns=2)
    assistant.register_tool("calc", lambda x, y: x + y)
    assistant.record_turn("Hello", "Hi there!", 100, 0.0003)
    ctx = assistant.build_message_context("How are you?")
    cost_msg = assistant.handle_slash_command("/cost")
    print(f"Assistant Demo Executed. Context Len: {len(ctx)}, Cost Msg: {cost_msg}")
    return ctx, cost_msg

if __name__ == "__main__":
    run_assistant_demo()

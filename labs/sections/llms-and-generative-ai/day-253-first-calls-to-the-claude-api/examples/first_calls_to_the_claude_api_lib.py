import os
import time
import random
from typing import Dict, Any, List, Optional

class RateLimitException(Exception): pass
class OverloadedException(Exception): pass
class FatalApiException(Exception): pass

class AnthropicClientWrapper:
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "sk-ant-mock-key-12345")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided.")
        self.max_retries = max_retries

    def compute_backoff(self, attempt: int, base_delay: float = 0.5, max_delay: float = 8.0) -> float:
        cap = min(max_delay, base_delay * (2 ** attempt))
        return random.uniform(0.5 * cap, cap)

    def create_message(
        self,
        model: str,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        max_tokens: int = 1024,
        _fail_count: int = 0
    ) -> Dict[str, Any]:
        if not messages or not isinstance(messages, list):
            raise FatalApiException("Messages must be a non-empty list.")
        for msg in messages:
            if msg.get("role") == "system":
                raise FatalApiException("System prompt must be passed as top-level 'system' parameter, not in messages.")

        # Simulate transient error recovery
        for attempt in range(self.max_retries):
            if attempt < _fail_count:
                sleep_dur = self.compute_backoff(attempt)
                # Sleep minimal in test
                continue

            return {
                "id": "msg_mock_99",
                "model": model,
                "system": system,
                "content": [{"type": "text", "text": "Diagnosis: Service healthy."}],
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 30, "output_tokens": 12}
            }

        raise RateLimitException("Max retries exceeded on transient rate limits.")

def run_client_demo():
    client = AnthropicClientWrapper()
    resp = client.create_message(
        model="claude-3-5-sonnet-20241022",
        system="You are an expert SRE.",
        messages=[{"role": "user", "content": "Check status."}],
        max_tokens=500
    )
    print("Anthropic Client Demo Executed. Stop reason:", resp["stop_reason"])
    return resp

if __name__ == "__main__":
    run_client_demo()

import time
import random
from typing import Dict, Any

class TokenBucket:
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_update = time.time()

    def consume(self, amount: float = 1.0) -> bool:
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)

        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False

class LLMCostLedger:
    PRICING = {
        "claude-3-5-sonnet": {"input": 3.00, "cache_read": 0.30, "output": 15.00},
        "gpt-4o": {"input": 2.50, "cache_read": 1.25, "output": 10.00}
    }

    def __init__(self):
        self.total_cost_usd = 0.0
        self.total_input_tokens = 0
        self.total_cached_tokens = 0
        self.total_output_tokens = 0

    def record_usage(self, model: str, input_tokens: int, cached_tokens: int, output_tokens: int) -> float:
        rates = self.PRICING.get(model, {"input": 3.0, "cache_read": 0.3, "output": 15.0})
        cost = (
            (input_tokens * rates["input"] / 1_000_000) +
            (cached_tokens * rates["cache_read"] / 1_000_000) +
            (output_tokens * rates["output"] / 1_000_000)
        )
        self.total_cost_usd += cost
        self.total_input_tokens += input_tokens
        self.total_cached_tokens += cached_tokens
        self.total_output_tokens += output_tokens
        return round(cost, 6)

def calculate_full_jitter_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 32.0) -> float:
    ceiling = min(max_delay, base_delay * (2 ** attempt))
    return random.uniform(0, ceiling)

def run_cost_demo():
    ledger = LLMCostLedger()
    cost = ledger.record_usage("claude-3-5-sonnet", 500, 10000, 200)
    bucket = TokenBucket(10, 2)
    consumed = bucket.consume(5)
    print(f"Cost Demo Executed. Cost: ${cost}, Token Consumed: {consumed}")
    return cost, consumed

if __name__ == "__main__":
    run_cost_demo()

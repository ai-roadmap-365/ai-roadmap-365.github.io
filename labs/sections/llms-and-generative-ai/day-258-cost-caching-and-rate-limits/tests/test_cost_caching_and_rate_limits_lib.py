import pytest
from examples.cost_caching_and_rate_limits_lib import (
    TokenBucket,
    LLMCostLedger,
    calculate_full_jitter_backoff
)

def test_cost_calculation():
    ledger = LLMCostLedger()
    # 500 input @ $3 = 0.0015, 10000 cached @ $0.3 = 0.003, 200 out @ $15 = 0.003 -> Total = 0.0075
    cost = ledger.record_usage("claude-3-5-sonnet", 500, 10000, 200)
    assert cost == 0.0075
    assert ledger.total_cost_usd == 0.0075
    assert ledger.total_cached_tokens == 10000

def test_token_bucket():
    bucket = TokenBucket(10, 1) # 10 capacity, 1 per sec
    assert bucket.consume(8) is True
    assert bucket.consume(5) is False # Only 2 left

def test_full_jitter_range():
    for _ in range(10):
        backoff = calculate_full_jitter_backoff(3, base_delay=1.0, max_delay=32.0)
        assert 0.0 <= backoff <= 8.0

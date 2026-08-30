import pytest
from examples.streaming_responses_lib import (
    StreamingTokenAggregator,
    simulate_mock_stream
)

def test_streaming_aggregation():
    aggregator = StreamingTokenAggregator()
    aggregator.start()
    for chunk in simulate_mock_stream():
        aggregator.process_chunk(chunk)
    result = aggregator.finish()

    assert result["text"] == "Real-time streaming slashes perceived latency drastically."
    assert result["token_count"] == 6
    assert result["ttft_ms"] > 0
    assert result["itl_ms"] > 0

def test_empty_stream():
    aggregator = StreamingTokenAggregator()
    aggregator.start()
    result = aggregator.finish()

    assert result["text"] == ""
    assert result["token_count"] == 0

def test_single_token_stream():
    aggregator = StreamingTokenAggregator()
    aggregator.start()
    aggregator.process_chunk("Hello")
    result = aggregator.finish()

    assert result["text"] == "Hello"
    assert result["token_count"] == 1

    # A chunk handed over with no delay legitimately has a time-to-first-token
    # of ~0. Asserting > 0 here asserts that the clock is slow, not that the
    # aggregator works. What must hold is that it is non-negative and inside
    # the total, and that one token means no inter-token gap.
    assert result["ttft_ms"] >= 0
    assert result["ttft_ms"] <= result["total_duration_ms"]
    assert result["itl_ms"] == 0.0

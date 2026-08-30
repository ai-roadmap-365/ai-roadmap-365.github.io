import pytest
from examples.first_calls_to_the_claude_api_lib import (
    AnthropicClientWrapper,
    RateLimitException,
    FatalApiException
)

def test_client_happy_path():
    client = AnthropicClientWrapper(api_key="sk-ant-test-key")
    resp = client.create_message(
        model="claude-3-5-sonnet-20241022",
        system="You are an auditor.",
        messages=[{"role": "user", "content": "Audit log"}],
        max_tokens=256
    )

    assert resp["stop_reason"] == "end_turn"
    assert resp["content"][0]["text"] == "Diagnosis: Service healthy."
    assert resp["usage"]["input_tokens"] > 0

def test_system_in_messages_raises_fatal():
    client = AnthropicClientWrapper()
    with pytest.raises(FatalApiException):
        client.create_message(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "system", "content": "Invalid placement"}]
        )

def test_retry_on_transient_failure():
    client = AnthropicClientWrapper(max_retries=3)
    # Simulate 2 transient fails before success
    resp = client.create_message(
        model="claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": "Retry test"}],
        _fail_count=2
    )
    assert resp["stop_reason"] == "end_turn"

def test_max_retries_exceeded():
    client = AnthropicClientWrapper(max_retries=2)
    with pytest.raises(RateLimitException):
        client.create_message(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": "Fail test"}],
            _fail_count=5
        )

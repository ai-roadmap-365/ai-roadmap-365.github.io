import pytest
from examples.full_stack_app import FullStackAIAppEngine

def test_normal_chat_request():
    app = FullStackAIAppEngine()
    res = app.process_chat_request("tenant_alpha", "sk_alpha_123", "Explain gravity")
    assert res["status"] == "SUCCESS"
    assert res["cached"] is False
    assert res["resolved_provider"] == "primary_claude"
    assert res["actual_cost_usd"] == 0.00465
    assert res["remaining_balance"] == 9.99535

def test_exact_cache_hit():
    app = FullStackAIAppEngine()
    res1 = app.process_chat_request("tenant_alpha", "sk_alpha_123", "Explain relativity")
    res2 = app.process_chat_request("tenant_alpha", "sk_alpha_123", "Explain relativity")
    assert res2["status"] == "SUCCESS"
    assert res2["cached"] is True
    assert res2["cost_usd"] == 0.0
    assert res2["remaining_balance"] == res1["remaining_balance"]

def test_payment_required_insufficient_credit():
    app = FullStackAIAppEngine()
    res = app.process_chat_request("tenant_poor", "sk_poor_123", "Complex prompt")
    assert res["status"] == "PAYMENT_REQUIRED"
    assert "Insufficient credit" in res["message"]

def test_multi_provider_failover():
    app = FullStackAIAppEngine()
    res = app.process_chat_request("tenant_alpha", "sk_alpha_123", "Tell story", simulated_failing_providers=["primary_claude"])
    assert res["status"] == "SUCCESS"
    assert res["resolved_provider"] == "secondary_openai"
    assert res["fallback_occurred"] is True

def test_upstream_outage_all_providers_fail():
    app = FullStackAIAppEngine()
    res = app.process_chat_request("tenant_alpha", "sk_alpha_123", "Tell story", simulated_failing_providers=["primary_claude", "secondary_openai", "backup_vllm"])
    assert res["status"] == "UPSTREAM_OUTAGE"
    # Ensure hold was released
    assert app.tenants["tenant_alpha"]["reserved_holds"] == 0.0

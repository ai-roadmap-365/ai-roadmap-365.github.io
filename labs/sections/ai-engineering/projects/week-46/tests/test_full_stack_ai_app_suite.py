import pytest
from examples.full_stack_ai_app_suite import FullStackAIAppSuite

def test_full_stack_chat_transaction():
    suite = FullStackAIAppSuite()
    suite.register_tenant("org_corp", "secret_key_1", balance=10.0)
    res = suite.execute_chat_transaction("org_corp", "secret_key_1", "What is quantum computing?")
    assert res["status"] == "SUCCESS"
    assert res["tier"] == "MODEL_GENERATION"
    assert res["resolved_provider"] == "primary_claude"
    assert res["actual_cost_usd"] == 0.00512
    assert res["remaining_balance"] == 9.99488

def test_exact_and_semantic_caching():
    suite = FullStackAIAppSuite()
    suite.register_tenant("org_corp", "secret_key_1", balance=10.0)
    res1 = suite.execute_chat_transaction("org_corp", "secret_key_1", "Explain gravity in physics")
    
    # Exact cache hit
    res2 = suite.execute_chat_transaction("org_corp", "secret_key_1", "Explain gravity in physics")
    assert res2["status"] == "SUCCESS"
    assert res2["tier"] == "TIER_1_EXACT_CACHE"
    assert res2["cost_usd"] == 0.0
    assert res2["remaining_balance"] == res1["remaining_balance"]

def test_insufficient_credit_rejection():
    suite = FullStackAIAppSuite()
    suite.register_tenant("org_empty", "key", balance=0.01)
    res = suite.execute_chat_transaction("org_empty", "key", "Test prompt")
    assert res["status"] == "PAYMENT_REQUIRED"
    assert "Insufficient credit" in res["message"]

def test_multi_provider_failover():
    suite = FullStackAIAppSuite()
    suite.register_tenant("org_corp", "key", balance=5.0)
    res = suite.execute_chat_transaction("org_corp", "key", "Complex query", simulated_failing_providers=["primary_claude"])
    assert res["status"] == "SUCCESS"
    assert res["resolved_provider"] == "secondary_openai"
    assert res["fallback_occurred"] is True
    assert res["attempted_providers"] == ["primary_claude", "secondary_openai"]

def test_all_providers_failed_hold_release():
    suite = FullStackAIAppSuite()
    suite.register_tenant("org_corp", "key", balance=5.0)
    res = suite.execute_chat_transaction(
        "org_corp",
        "key",
        "Test prompt",
        simulated_failing_providers=["primary_claude", "secondary_openai", "backup_vllm"]
    )
    assert res["status"] == "UPSTREAM_OUTAGE"
    assert suite.tenants["org_corp"]["reserved_holds"] == 0.0
    assert suite.tenants["org_corp"]["balance"] == 5.0

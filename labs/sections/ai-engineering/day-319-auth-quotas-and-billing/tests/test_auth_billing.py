import pytest
from examples.auth_billing import AuthBillingEngine

def test_register_and_pre_auth():
    engine = AuthBillingEngine()
    engine.register_tenant("org_alpha", "sk_test_123", initial_credits=10.0)
    ok, msg, hold_id = engine.authenticate_and_reserve_hold("org_alpha", "sk_test_123", estimated_cost=0.05)
    assert ok is True
    assert msg == "HOLD_RESERVED"
    assert hold_id is not None
    assert engine.tenants["org_alpha"]["reserved_holds"] == 0.05

def test_invalid_api_key_rejection():
    engine = AuthBillingEngine()
    engine.register_tenant("org_alpha", "sk_test_123", initial_credits=10.0)
    ok, msg, hold = engine.authenticate_and_reserve_hold("org_alpha", "wrong_key")
    assert ok is False
    assert "Invalid API Key" in msg

def test_insufficient_available_balance():
    engine = AuthBillingEngine()
    engine.register_tenant("org_poor", "key", initial_credits=0.01)
    ok, msg, hold = engine.authenticate_and_reserve_hold("org_poor", "key", estimated_cost=0.05)
    assert ok is False
    assert "Insufficient available credit" in msg

def test_rate_limit_rpm_enforcement():
    engine = AuthBillingEngine()
    engine.register_tenant("org_limited", "key", initial_credits=10.0, rpm_limit=2)
    ok1, _, h1 = engine.authenticate_and_reserve_hold("org_limited", "key", 0.01)
    ok2, _, h2 = engine.authenticate_and_reserve_hold("org_limited", "key", 0.01)
    ok3, msg3, _ = engine.authenticate_and_reserve_hold("org_limited", "key", 0.01)
    assert ok1 is True
    assert ok2 is True
    assert ok3 is False
    assert "RPM limit reached" in msg3

def test_settle_token_usage():
    engine = AuthBillingEngine()
    engine.register_tenant("org_1", "key", initial_credits=5.0)
    _, _, hold_id = engine.authenticate_and_reserve_hold("org_1", "key", estimated_cost=0.05)
    
    # 1000 prompt tokens ($0.003) + 200 completion tokens ($0.003) = $0.006
    settle = engine.settle_token_usage(hold_id, prompt_tokens=1000, completion_tokens=200)
    assert settle["status"] == "SETTLED"
    assert settle["actual_cost_usd"] == 0.006
    assert settle["remaining_balance"] == 4.994
    assert engine.tenants["org_1"]["reserved_holds"] == 0.0

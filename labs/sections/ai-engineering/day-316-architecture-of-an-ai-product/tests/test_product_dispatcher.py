import pytest
from examples.product_dispatcher import AIProductDispatcher

def test_valid_dispatch_and_credit_deduction():
    dispatcher = AIProductDispatcher()
    res = dispatcher.dispatch_chat("org_alpha", "Tell me a joke")
    assert res["status"] == "SUCCESS"
    assert len(res["tokens_streamed"]) > 0
    assert res["cached"] is False
    assert res["remaining_credits"] == 49.998

def test_cached_query_zero_cost():
    dispatcher = AIProductDispatcher()
    res1 = dispatcher.dispatch_chat("org_alpha", "Summarize article")
    res2 = dispatcher.dispatch_chat("org_alpha", "Summarize article")
    assert res2["status"] == "CACHED"
    assert res2["cached"] is True
    assert res2["cost_usd"] == 0.0
    assert res2["remaining_credits"] == 49.998

def test_unauthorized_tenant():
    dispatcher = AIProductDispatcher()
    res = dispatcher.dispatch_chat("org_unknown", "Hello")
    assert res["status"] == "ERROR"
    assert "Unauthorized" in res["error_code"]

def test_zero_credit_rejection():
    dispatcher = AIProductDispatcher()
    res = dispatcher.dispatch_chat("org_beta", "Generate report")
    assert res["status"] == "ERROR"
    assert "Payment Required" in res["error_code"]

def test_rate_limit_rejection():
    dispatcher = AIProductDispatcher()
    # org_gamma has limit of 2 requests/min
    res1 = dispatcher.dispatch_chat("org_gamma", "Q1")
    res2 = dispatcher.dispatch_chat("org_gamma", "Q2")
    res3 = dispatcher.dispatch_chat("org_gamma", "Q3")
    assert res1["status"] == "SUCCESS"
    assert res2["status"] == "SUCCESS"
    assert res3["status"] == "ERROR"
    assert "Rate limit exceeded" in res3["error_code"]

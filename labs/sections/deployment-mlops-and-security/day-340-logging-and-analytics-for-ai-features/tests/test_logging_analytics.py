import pytest
from examples.logging_analytics import AIStructuredLoggingAnalyticsEngine

def test_pii_sanitization():
    engine = AIStructuredLoggingAnalyticsEngine()
    raw = "Contact alice@corp.com, SSN 123-45-6789, CC 4111-2222-3333-4444."
    cleaned = engine.sanitize_pii(raw)
    
    assert "alice@corp.com" not in cleaned
    assert "[REDACTED_EMAIL]" in cleaned
    assert "123-45-6789" not in cleaned
    assert "[REDACTED_SSN]" in cleaned
    assert "4111-2222-3333-4444" not in cleaned
    assert "[REDACTED_CC]" in cleaned

def test_structured_log_emission_with_trace():
    engine = AIStructuredLoggingAnalyticsEngine()
    custom_trace = "trace_abc_123"
    rec = engine.log_inference_event(
        tenant_id="tenant_fintech",
        prompt="Query account for bob@fin.com",
        completion="Account balance is $5,000",
        prompt_tokens=1000,
        completion_tokens=500,
        trace_id=custom_trace
    )
    
    assert rec["trace_id"] == custom_trace
    assert rec["tenant_id"] == "tenant_fintech"
    assert rec["prompt_tokens"] == 1000
    assert rec["completion_tokens"] == 500
    assert rec["total_tokens"] == 1500
    assert "[REDACTED_EMAIL]" in rec["prompt_sanitized"]

def test_cost_calculation():
    # Prompt: $0.002 per 1k ($0.000002/tok), Comp: $0.006 per 1k ($0.000006/tok)
    engine = AIStructuredLoggingAnalyticsEngine(prompt_cost_per_1k=0.002, completion_cost_per_1k=0.006)
    rec = engine.log_inference_event("t1", "p", "c", prompt_tokens=1000, completion_tokens=1000)
    
    # 1000 * 0.000002 = 0.002, 1000 * 0.000006 = 0.006 -> Total: 0.008
    assert rec["cost_usd"] == 0.008

def test_multi_tenant_ledger_aggregation():
    engine = AIStructuredLoggingAnalyticsEngine(prompt_cost_per_1k=0.002, completion_cost_per_1k=0.006)
    engine.log_inference_event("tenant_a", "p1", "c1", 1000, 500) # cost = 0.002 + 0.003 = 0.005
    engine.log_inference_event("tenant_a", "p2", "c2", 500, 500)  # cost = 0.001 + 0.003 = 0.004
    engine.log_inference_event("tenant_b", "p3", "c3", 2000, 1000) # cost = 0.004 + 0.006 = 0.010
    
    assert engine.tenant_ledger["tenant_a"]["total_requests"] == 2
    assert engine.tenant_ledger["tenant_a"]["total_prompt_tokens"] == 1500
    assert engine.tenant_ledger["tenant_a"]["total_cost_usd"] == 0.009
    
    assert engine.tenant_ledger["tenant_b"]["total_requests"] == 1
    assert engine.tenant_ledger["tenant_b"]["total_cost_usd"] == 0.010

def test_auto_generated_trace_id():
    engine = AIStructuredLoggingAnalyticsEngine()
    rec = engine.log_inference_event("t1", "p", "c", 10, 10)
    assert len(rec["trace_id"]) == 32 # Hex UUID

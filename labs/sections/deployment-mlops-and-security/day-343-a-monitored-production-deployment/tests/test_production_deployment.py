import pytest
from examples.production_deployment import UnifiedProductionAIPlatform

def test_pii_sanitization_and_trace_injection():
    platform = UnifiedProductionAIPlatform()
    res = platform.execute_inference("tenant_1", "user_1", "User email is alice@corp.com and SSN is 111-22-3333.")
    
    assert "[REDACTED_EMAIL]" in res["prompt_sanitized"]
    assert "[REDACTED_SSN]" in res["prompt_sanitized"]
    assert len(res["trace_id"]) == 32

def test_cost_attribution_ledger():
    platform = UnifiedProductionAIPlatform()
    # 1000 prompt * 0.000002 = 0.002, 500 comp * 0.000006 = 0.003 -> Total 0.005
    platform.execute_inference("tenant_fin", "u1", "p1", prompt_tokens=1000, completion_tokens=500)
    platform.execute_inference("tenant_fin", "u2", "p2", prompt_tokens=1000, completion_tokens=500)
    
    assert platform.tenant_ledger["tenant_fin"] == 0.010

def test_observability_report_percentiles():
    platform = UnifiedProductionAIPlatform()
    for lat in [100.0, 120.0, 140.0, 160.0, 500.0]:
        platform.execute_inference("t1", "u1", "p", latency_ms=lat)
        
    rep = platform.get_observability_report()
    assert rep["total_requests"] == 5
    assert rep["p50_latency_ms"] == 140.0
    assert rep["p95_latency_ms"] == 432.0

def test_automated_circuit_breaker_rollback_on_error_spike():
    platform = UnifiedProductionAIPlatform(canary_pct=100, error_threshold_pct=10.0, min_eval_requests=10)
    
    # 8 success, 4 errors = 33.3% > 10%
    for _ in range(8):
        platform.execute_inference("t1", "u1", "good", simulate_error=False)
    for _ in range(4):
        platform.execute_inference("t1", "u1", "bad", simulate_error=True)
        
    rep = platform.get_observability_report()
    assert rep["circuit_tripped"] is True
    assert platform.circuit_tripped is True
    
    # Next inference should automatically receive BASELINE_V1 due to tripped circuit
    rec = platform.execute_inference("t1", "u1", "next query")
    assert rec["variant"] == "BASELINE_V1"

def test_empty_platform_report():
    platform = UnifiedProductionAIPlatform()
    rep = platform.get_observability_report()
    assert rep["total_requests"] == 0
    assert rep["p50_latency_ms"] == 0.0
    assert rep["circuit_tripped"] is False

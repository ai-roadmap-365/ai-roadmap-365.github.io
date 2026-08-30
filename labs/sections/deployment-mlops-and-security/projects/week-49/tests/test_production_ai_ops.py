import pytest
from examples.production_ai_ops import ProductionAIOpsPlatform

def test_pii_sanitization_full():
    platform = ProductionAIOpsPlatform()
    raw = "User bob@corp.com with SSN 000-11-2222 and CC 4111-2222-3333-4444."
    cleaned = platform.sanitize_pii(raw)
    
    assert "[REDACTED_EMAIL]" in cleaned
    assert "[REDACTED_SSN]" in cleaned
    assert "[REDACTED_CC]" in cleaned

def test_deterministic_variant_routing():
    platform = ProductionAIOpsPlatform(canary_pct=50)
    v1 = platform._get_variant("user_alpha")
    v2 = platform._get_variant("user_alpha")
    assert v1 == v2

def test_multi_tenant_financial_ledger():
    platform = ProductionAIOpsPlatform()
    platform.execute_inference("tenant_alpha", "u1", "p", 1000, 1000) # 0.008
    platform.execute_inference("tenant_beta", "u2", "p", 2000, 1000)  # 0.010
    
    telemetry = platform.get_platform_telemetry()
    assert telemetry["total_tenants"] == 2
    assert telemetry["total_spend_usd"] == 0.018

def test_percentile_latencies():
    platform = ProductionAIOpsPlatform()
    for lat in range(1, 101):
        platform.execute_inference("t1", f"u{lat}", "p", latency_ms=float(lat))
        
    telemetry = platform.get_platform_telemetry()
    assert telemetry["p50_latency_ms"] == 50.5
    assert telemetry["p95_latency_ms"] == 95.05
    assert telemetry["p99_latency_ms"] == 99.01

def test_automated_circuit_breaker_trip():
    platform = ProductionAIOpsPlatform(canary_pct=100, error_threshold_pct=5.0, min_eval_requests=10)
    for _ in range(8):
        platform.execute_inference("t1", "u1", "p", simulate_error=False)
    for _ in range(4):
        platform.execute_inference("t1", "u1", "p", simulate_error=True)
        
    assert platform.circuit_tripped is True
    assert platform.get_platform_telemetry()["circuit_tripped"] is True
    
    # Post-trip traffic routes to BASELINE_V1
    rec = platform.execute_inference("t1", "u1", "post trip")
    assert rec["variant"] == "BASELINE_V1"

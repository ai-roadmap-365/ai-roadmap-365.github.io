import pytest
from examples.monitoring_alerting import AIObservabilityAlertEngine

def test_percentile_calculation():
    engine = AIObservabilityAlertEngine(p95_ttft_threshold_ms=300.0)
    # 100 uniform samples from 1 to 100
    for val in range(1, 101):
        engine.record_inference_event(float(val))
        
    metrics = engine.evaluate_metrics()
    assert metrics["p50_ttft_ms"] == 50.5
    assert metrics["p95_ttft_ms"] == 95.05
    assert metrics["active_alert_count"] == 0

def test_high_tail_latency_alert_trigger():
    engine = AIObservabilityAlertEngine(p95_ttft_threshold_ms=200.0)
    # 90 normal requests at 50ms, 10 tail requests at 500ms
    for _ in range(90):
        engine.record_inference_event(50.0)
    for _ in range(10):
        engine.record_inference_event(500.0)
        
    metrics = engine.evaluate_metrics()
    assert metrics["p95_ttft_ms"] > 200.0
    assert metrics["active_alert_count"] == 1
    assert engine.active_alerts[0]["alert_name"] == "HighTailLatencyP95"
    assert engine.active_alerts[0]["severity"] == "CRITICAL"

def test_error_rate_alert_trigger():
    engine = AIObservabilityAlertEngine(error_rate_threshold_pct=2.0)
    # 95 successful, 5 errors = 5% error rate > 2% threshold
    for _ in range(95):
        engine.record_inference_event(100.0, is_error=False)
    for _ in range(5):
        engine.record_inference_event(0.0, is_error=True)
        
    metrics = engine.evaluate_metrics()
    assert metrics["error_rate_pct"] == 5.0
    assert metrics["active_alert_count"] == 1
    assert engine.active_alerts[0]["alert_name"] == "HighInferenceErrorRate"

def test_healthy_traffic_zero_alerts():
    engine = AIObservabilityAlertEngine(p95_ttft_threshold_ms=300.0, error_rate_threshold_pct=1.0)
    for _ in range(100):
        engine.record_inference_event(120.0, is_error=False)
        
    metrics = engine.evaluate_metrics()
    assert metrics["active_alert_count"] == 0
    assert len(engine.active_alerts) == 0

def test_empty_metrics_handling():
    engine = AIObservabilityAlertEngine()
    metrics = engine.evaluate_metrics()
    assert metrics["total_requests"] == 0
    assert metrics["p50_ttft_ms"] == 0.0
    assert metrics["active_alert_count"] == 0

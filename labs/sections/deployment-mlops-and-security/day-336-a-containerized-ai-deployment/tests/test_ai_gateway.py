import pytest
from examples.ai_gateway import ProductionAIGateway

def test_lor_load_balancing_selects_least_active():
    gateway = ProductionAIGateway()
    gateway.register_replica("gpu_1")
    gateway.register_replica("gpu_2")
    
    # First request goes to gpu_1 (active 0 -> 1)
    res1 = gateway.route_request("p1", 100.0)
    assert res1["status"] == "ROUTED"
    assert res1["assigned_replica"] == "gpu_1"
    
    # Second request goes to gpu_2 (active 0 < active 1)
    res2 = gateway.route_request("p2", 100.1)
    assert res2["status"] == "ROUTED"
    assert res2["assigned_replica"] == "gpu_2"

def test_active_request_decrement_on_complete():
    gateway = ProductionAIGateway()
    gateway.register_replica("gpu_1")
    gateway.route_request("p1", 100.0)
    assert gateway.replicas["gpu_1"].active_requests == 1
    
    gateway.complete_request("gpu_1", success=True, current_time=101.0)
    assert gateway.replicas["gpu_1"].active_requests == 0

def test_circuit_breaker_tripping_on_consecutive_failures():
    gateway = ProductionAIGateway(failure_threshold=2)
    gateway.register_replica("gpu_1")
    
    gateway.route_request("p1", 100.0)
    gateway.complete_request("gpu_1", success=False, current_time=100.5)
    assert gateway.replicas["gpu_1"].is_healthy is True
    
    gateway.route_request("p2", 101.0)
    gateway.complete_request("gpu_1", success=False, current_time=101.5)
    assert gateway.replicas["gpu_1"].is_healthy is False
    assert gateway.circuit_state == "OPEN"

def test_circuit_breaker_open_returns_fallback():
    gateway = ProductionAIGateway(failure_threshold=1, cooldown_seconds=10.0)
    gateway.register_replica("gpu_1")
    gateway.route_request("p1", 100.0)
    gateway.complete_request("gpu_1", success=False, current_time=101.0) # Tripped to OPEN
    
    # Attempt request during cooldown
    res = gateway.route_request("p2", 105.0)
    assert res["status"] == "FALLBACK"
    assert "fallback" in res["response"].lower()

def test_circuit_breaker_half_open_recovery():
    gateway = ProductionAIGateway(failure_threshold=1, cooldown_seconds=10.0)
    gateway.register_replica("gpu_1")
    gateway.route_request("p1", 100.0)
    gateway.complete_request("gpu_1", success=False, current_time=101.0)
    
    # Restore health for probe test
    gateway.replicas["gpu_1"].is_healthy = True
    
    # At t=115 (14s > 10s cooldown), next request transitions to HALF_OPEN
    res = gateway.route_request("probe", 115.0)
    assert res["status"] == "ROUTED"
    assert res["circuit_state"] == "HALF_OPEN"
    
    # Successful probe resets to CLOSED
    gateway.complete_request("gpu_1", success=True, current_time=116.0)
    assert gateway.circuit_state == "CLOSED"

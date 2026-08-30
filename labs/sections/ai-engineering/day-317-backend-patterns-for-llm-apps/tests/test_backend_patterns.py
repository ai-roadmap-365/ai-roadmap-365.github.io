import pytest
import time
from examples.backend_patterns import ResilientLLMBackend

def test_successful_request():
    backend = ResilientLLMBackend()
    res = backend.process_request("key_1", "What is Python?")
    assert res["status"] == "SUCCESS"
    assert res["provider"] == "primary_model"
    assert res["cached"] is False

def test_idempotent_replay():
    backend = ResilientLLMBackend()
    res1 = backend.process_request("key_2", "Prompt A")
    res2 = backend.process_request("key_2", "Prompt A")
    assert res2["status"] == "REPLAYED"
    assert res2["cached"] is True
    assert res2["response"] == res1["response"]

def test_circuit_trips_to_open():
    backend = ResilientLLMBackend(failure_threshold=2)
    # 2 failures
    backend.process_request("k_err1", "P1", simulate_upstream_fail=True)
    backend.process_request("k_err2", "P2", simulate_upstream_fail=True)
    assert backend.state == "OPEN"

def test_fallback_routing_when_open():
    backend = ResilientLLMBackend(failure_threshold=1)
    backend.process_request("k_err", "P1", simulate_upstream_fail=True)
    assert backend.state == "OPEN"
    
    res = backend.process_request("k_fall", "P2", simulate_upstream_fail=False)
    assert res["status"] == "CIRCUIT_OPEN_FALLBACK"
    assert res["provider"] == "backup_replica"

def test_self_healing_recovery():
    backend = ResilientLLMBackend(failure_threshold=1, reset_timeout_seconds=0.05)
    backend.process_request("k_err", "P1", simulate_upstream_fail=True)
    assert backend.state == "OPEN"
    
    time.sleep(0.06)
    assert backend.check_circuit_state() == "HALF-OPEN"
    
    res = backend.process_request("k_probe", "P_probe", simulate_upstream_fail=False)
    assert res["status"] == "SUCCESS"
    assert backend.state == "CLOSED"
    assert backend.failure_count == 0

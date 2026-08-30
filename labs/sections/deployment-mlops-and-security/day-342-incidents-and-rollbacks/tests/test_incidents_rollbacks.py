import pytest
from examples.incidents_rollbacks import AIIncidentRollbackEngine

def test_initial_circuit_breaker_state():
    engine = AIIncidentRollbackEngine()
    assert engine.active_variant == "CANDIDATE_V2"
    assert engine.circuit_tripped is False
    assert len(engine.incident_log) == 0

def test_healthy_traffic_keeps_circuit_closed():
    engine = AIIncidentRollbackEngine(error_threshold_pct=5.0, min_requests_to_evaluate=10)
    for _ in range(15):
        engine.record_request_outcome(is_error=False)
        
    assert engine.circuit_tripped is False
    assert engine.active_variant == "CANDIDATE_V2"
    assert "CANDIDATE_V2" in engine.route_inference("Query")

def test_error_rate_spike_trips_circuit_and_reverts():
    engine = AIIncidentRollbackEngine(error_threshold_pct=5.0, min_requests_to_evaluate=10)
    # 8 success, 4 failures = 33.3% > 5.0%
    for _ in range(8):
        engine.record_request_outcome(is_error=False)
    for _ in range(4):
        engine.record_request_outcome(is_error=True)
        
    assert engine.circuit_tripped is True
    assert engine.active_variant == "BASELINE_V1"
    assert "BASELINE_V1" in engine.route_inference("Query")
    assert len(engine.incident_log) == 1
    assert engine.incident_log[0]["action"] == "CIRCUIT_BREAKER_ROLLBACK"

def test_min_requests_guard_prevents_premature_trip():
    engine = AIIncidentRollbackEngine(error_threshold_pct=5.0, min_requests_to_evaluate=10)
    # 1 request that fails -> 100% error rate, but < 10 min requests -> do not trip yet!
    engine.record_request_outcome(is_error=True)
    
    assert engine.circuit_tripped is False
    assert engine.active_variant == "CANDIDATE_V2"

def test_post_trip_ignores_further_candidate_errors():
    engine = AIIncidentRollbackEngine(error_threshold_pct=5.0, min_requests_to_evaluate=2)
    engine.record_request_outcome(is_error=True)
    engine.record_request_outcome(is_error=True) # Trips here
    
    assert engine.circuit_tripped is True
    assert len(engine.incident_log) == 1
    
    # Additional recordings should be ignored since circuit is already tripped
    engine.record_request_outcome(is_error=True)
    assert len(engine.incident_log) == 1

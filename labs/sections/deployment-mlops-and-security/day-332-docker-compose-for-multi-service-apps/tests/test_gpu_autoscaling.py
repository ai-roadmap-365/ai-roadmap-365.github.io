import pytest
from examples.gpu_autoscaling import GPUAutoscalingDecisionEngine

def test_immediate_scale_up_on_queue_spike():
    engine = GPUAutoscalingDecisionEngine(min_replicas=1, max_replicas=10, target_waiting_per_pod=5)
    # 23 waiting requests -> ceil(23/5) = 5 pods
    res = engine.calculate_desired_replicas(waiting_requests=23, current_timestamp=100.0)
    assert res["action"] == "SCALE_UP"
    assert res["old_replicas"] == 1
    assert res["new_replicas"] == 5
    assert engine.current_replicas == 5

def test_max_replica_clamping():
    engine = GPUAutoscalingDecisionEngine(min_replicas=1, max_replicas=4, target_waiting_per_pod=5)
    # 50 waiting requests -> wants 10 pods, clamped to max 4
    res = engine.calculate_desired_replicas(waiting_requests=50, current_timestamp=100.0)
    assert res["action"] == "SCALE_UP"
    assert res["new_replicas"] == 4
    assert engine.current_replicas == 4

def test_scale_down_cooldown_hold():
    engine = GPUAutoscalingDecisionEngine(min_replicas=1, max_replicas=10, target_waiting_per_pod=5, scale_down_cooldown_seconds=300)
    engine.calculate_desired_replicas(25, 100.0) # Scale up to 5
    
    # Queue drops to 0 at t=110
    res1 = engine.calculate_desired_replicas(0, 110.0)
    assert res1["action"] == "HOLD_COOLDOWN"
    assert engine.current_replicas == 5
    
    # At t=200 (90s in cooldown), still holding
    res2 = engine.calculate_desired_replicas(0, 200.0)
    assert res2["action"] == "HOLD_COOLDOWN"
    assert engine.current_replicas == 5

def test_scale_down_after_cooldown_expires():
    engine = GPUAutoscalingDecisionEngine(min_replicas=1, max_replicas=10, target_waiting_per_pod=5, scale_down_cooldown_seconds=100)
    engine.calculate_desired_replicas(20, 100.0) # Current = 4
    engine.calculate_desired_replicas(0, 105.0)  # Start cooldown at t=105
    
    # At t=210 (105s elapsed > 100s cooldown), scale down executes!
    res = engine.calculate_desired_replicas(0, 210.0)
    assert res["action"] == "SCALE_DOWN"
    assert res["old_replicas"] == 4
    assert res["new_replicas"] == 1
    assert engine.current_replicas == 1

def test_no_change_when_load_matches_replicas():
    engine = GPUAutoscalingDecisionEngine(min_replicas=2, max_replicas=5, target_waiting_per_pod=5)
    engine.current_replicas = 2
    res = engine.calculate_desired_replicas(waiting_requests=8, current_timestamp=100.0) # ceil(8/5) = 2
    assert res["action"] == "NO_CHANGE"
    assert res["current_replicas"] == 2

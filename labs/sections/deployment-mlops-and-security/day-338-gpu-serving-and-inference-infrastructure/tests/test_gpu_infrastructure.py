import pytest
from examples.gpu_infrastructure import GPUServingInfrastructureSimulator

def test_vram_allocation_and_oom_protection():
    sim = GPUServingInfrastructureSimulator()
    assert sim.load_model_to_vram("embed_model", 8192) is True
    assert sim.load_model_to_vram("rerank_model", 8192) is True
    # Total 16384 MB full -> next model should fail OOM
    assert sim.load_model_to_vram("extra_model", 1024) is False

def test_dynamic_batch_full_immediate_dispatch():
    sim = GPUServingInfrastructureSimulator(max_batch_size=3, max_queue_delay_ms=10.0)
    sim.enqueue_request("r1", "prompt 1", 100.000)
    sim.enqueue_request("r2", "prompt 2", 100.001)
    sim.enqueue_request("r3", "prompt 3", 100.002)
    
    # 3 items >= max_batch_size (3) -> dispatches immediately at t=100.003
    res = sim.process_dynamic_batch(current_time=100.003)
    assert res is not None
    assert res["batch_size"] == 3
    assert res["request_ids"] == ["r1", "r2", "r3"]
    assert len(sim.incoming_queue) == 0

def test_dynamic_batch_queue_delay_timeout_flush():
    sim = GPUServingInfrastructureSimulator(max_batch_size=5, max_queue_delay_ms=5.0)
    sim.enqueue_request("r1", "prompt 1", 100.000)
    
    # At t=100.002 (2ms < 5ms delay and 1 < 5 batch), should hold
    assert sim.process_dynamic_batch(current_time=100.002) is None
    
    # At t=100.006 (6ms > 5ms delay), should flush single-item batch!
    res = sim.process_dynamic_batch(current_time=100.006)
    assert res is not None
    assert res["batch_size"] == 1
    assert res["request_ids"] == ["r1"]

def test_empty_queue_returns_none():
    sim = GPUServingInfrastructureSimulator()
    assert sim.process_dynamic_batch(100.0) is None

def test_partial_batch_draining_when_exceeding_max_batch():
    sim = GPUServingInfrastructureSimulator(max_batch_size=2, max_queue_delay_ms=10.0)
    sim.enqueue_request("r1", "p1", 100.0)
    sim.enqueue_request("r2", "p2", 100.0)
    sim.enqueue_request("r3", "p3", 100.0)
    
    res = sim.process_dynamic_batch(100.001)
    assert res["batch_size"] == 2
    assert len(sim.incoming_queue) == 1

import pytest
from examples.deployed_system import DeployedAISystem, ServingWorker, PagedCache

def test_paged_cache_allocation_and_free():
    cache = PagedCache(total_blocks=4, block_size=4)
    assert cache.allocate("r1", 7) is True  # Needs 2 blocks
    assert len(cache.free_blocks) == 2
    
    cache.free("r1")
    assert len(cache.free_blocks) == 4

def test_lor_load_balancing_distribution():
    system = DeployedAISystem(num_workers=2)
    # Route 1 goes to worker_0 (active 0 -> 1)
    res1 = system.route_request("r1", prompt_tokens=4, max_tokens=2)
    assert res1["status"] == "ACCEPTED"
    assert res1["worker_id"] == "worker_0"
    
    # Route 2 goes to worker_1 (active 0 < 1)
    res2 = system.route_request("r2", prompt_tokens=4, max_tokens=2)
    assert res2["status"] == "ACCEPTED"
    assert res2["worker_id"] == "worker_1"

def test_continuous_batch_stepping_and_completion():
    system = DeployedAISystem(num_workers=1)
    system.route_request("short_req", prompt_tokens=4, max_tokens=1)
    system.route_request("long_req", prompt_tokens=4, max_tokens=3)
    
    # Step 1: short_req completes
    step1 = system.step_all()
    assert step1["worker_0"] == ["short_req"]
    assert len(system.workers[0].active_batch) == 1
    
    # Step 2: long_req still running
    step2 = system.step_all()
    assert step2["worker_0"] == []
    
    # Step 3: long_req finishes
    step3 = system.step_all()
    assert step3["worker_0"] == ["long_req"]
    assert len(system.workers[0].active_batch) == 0

def test_circuit_breaker_on_all_workers_unhealthy():
    system = DeployedAISystem(num_workers=2)
    for w in system.workers:
        w.is_healthy = False
        
    res = system.route_request("r1", 4, 2)
    assert res["status"] == "CIRCUIT_FALLBACK"
    assert system.circuit_state == "OPEN"

def test_vram_saturation_throttling():
    # Worker with only 1 block (4 tokens)
    system = DeployedAISystem(num_workers=1)
    system.workers[0].cache = PagedCache(total_blocks=1, block_size=4)
    
    # First request takes 1 block
    res1 = system.route_request("r1", 4, 2)
    assert res1["status"] == "ACCEPTED"
    
    # Second request throttled
    res2 = system.route_request("r2", 4, 2)
    assert res2["status"] == "VRAM_THROTTLED"

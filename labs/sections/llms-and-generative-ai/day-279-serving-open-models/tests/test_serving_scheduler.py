import pytest
from serving_scheduler import PagedBlockAllocator, RequestState, ContinuousBatchScheduler

@pytest.fixture
def allocator():
    return PagedBlockAllocator(num_blocks=32, block_size=16)

def test_block_allocator_lifecycle(allocator):
    assert len(allocator.free_blocks) == 32
    b1 = allocator.allocate_block()
    b2 = allocator.allocate_block()
    assert b1 == 0 and b2 == 1
    assert len(allocator.free_blocks) == 30
    assert len(allocator.allocated_blocks) == 2

    allocator.free_block(b1)
    assert len(allocator.free_blocks) == 31
    assert b1 not in allocator.allocated_blocks

def test_continuous_batching_step_and_eviction(allocator):
    scheduler = ContinuousBatchScheduler(allocator, max_batch_size=2)
    # Req 1 needs 2 tokens, Req 2 needs 5 tokens
    r1 = RequestState("req_1", prompt_len=10, target_gen_len=2)
    r2 = RequestState("req_2", prompt_len=10, target_gen_len=5)
    
    scheduler.add_request(r1)
    scheduler.add_request(r2)

    # Step 1: Both admitted
    s1 = scheduler.step_iteration()
    assert s1["active_requests"] == 2
    assert s1["completed_requests"] == 0

    # Step 2: Req 1 completes, evicted from active batch
    s2 = scheduler.step_iteration()
    assert len(scheduler.completed_requests) == 1
    assert scheduler.completed_requests[0].request_id == "req_1"
    assert len(scheduler.running_batch) == 1

def test_dynamic_block_expansion(allocator):
    scheduler = ContinuousBatchScheduler(allocator, max_batch_size=1)
    # Prompt is 15 tokens (1 block). Target gen is 20 tokens -> Total 35 tokens (needs 3 blocks)
    r = RequestState("req_large", prompt_len=15, target_gen_len=20)
    scheduler.add_request(r)

    # Initial step
    scheduler.step_iteration()
    assert len(r.block_table) == 1

    # Run remaining steps
    for _ in range(19):
        scheduler.step_iteration()

    assert r.completed is True
    # All blocks should be freed on completion
    assert len(allocator.allocated_blocks) == 0

def test_out_of_memory_error(allocator):
    # Exhaust all 32 blocks
    for _ in range(32):
        allocator.allocate_block()
    with pytest.raises(MemoryError, match="Out of Memory"):
        allocator.allocate_block()

def test_fragmentation_metrics(allocator):
    scheduler = ContinuousBatchScheduler(allocator, max_batch_size=4)
    r = RequestState("req_1", prompt_len=14, target_gen_len=10) # Total 24 tokens (needs 2 blocks = 32 slots)
    scheduler.add_request(r)
    scheduler.step_iteration()
    scheduler.step_iteration()
    scheduler.step_iteration()

    metrics = scheduler.compute_fragmentation_metrics(max_context_window=128)
    assert metrics["paged_used_blocks"] == 2.0
    # Paged waste is (32 - 17) / 32 = 46.8%
    # Static waste is (128 - 17) / 128 = 86.7%
    assert metrics["paged_waste_percentage"] < metrics["static_waste_percentage"]

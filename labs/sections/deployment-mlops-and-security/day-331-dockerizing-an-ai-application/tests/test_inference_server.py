import pytest
from examples.inference_server import PagedKVCacheManager, ContinuousBatchScheduler

def test_paged_kv_cache_allocation_and_free():
    cache = PagedKVCacheManager(total_blocks=8, block_size_tokens=4)
    assert len(cache.free_blocks) == 8
    
    # 7 tokens needs 2 blocks (size 4)
    res = cache.allocate_for_request("req1", 7)
    assert res is True
    assert len(cache.block_tables["req1"]) == 2
    assert len(cache.free_blocks) == 6
    
    cache.free_request("req1")
    assert len(cache.free_blocks) == 8
    assert "req1" not in cache.block_tables

def test_continuous_batch_short_request_early_exit():
    cache = PagedKVCacheManager(total_blocks=10, block_size_tokens=4)
    scheduler = ContinuousBatchScheduler(cache)
    
    scheduler.add_request("req_short", prompt_tokens=4, max_tokens=1) # 1 token
    scheduler.add_request("req_long", prompt_tokens=4, max_tokens=4)  # 4 tokens
    
    # Step 1: both admitted, req_short generates 1 token and finishes!
    done1 = scheduler.step()
    assert done1 == ["req_short"]
    assert len(scheduler.running_batch) == 1
    assert scheduler.running_batch[0]["req_id"] == "req_long"

def test_vram_saturation_throttles_admission():
    cache = PagedKVCacheManager(total_blocks=2, block_size_tokens=4)
    scheduler = ContinuousBatchScheduler(cache)
    
    # Each request takes 1 block (4 tokens)
    scheduler.add_request("r1", prompt_tokens=4, max_tokens=3)
    scheduler.add_request("r2", prompt_tokens=4, max_tokens=3)
    scheduler.add_request("r3", prompt_tokens=4, max_tokens=3) # Should wait
    
    scheduler.step()
    assert len(scheduler.running_batch) == 2
    assert len(scheduler.waiting_queue) == 1
    assert scheduler.waiting_queue[0]["req_id"] == "r3"

def test_token_append_allocates_new_blocks():
    cache = PagedKVCacheManager(total_blocks=4, block_size_tokens=4)
    cache.allocate_for_request("req_grow", 4) # 1 block
    assert len(cache.block_tables["req_grow"]) == 1
    
    # Adding 4th token reaches multiple of 4, allocating next block
    cache.append_token("req_grow", 8)
    assert len(cache.block_tables["req_grow"]) == 2
    assert len(cache.free_blocks) == 2

def test_batch_drains_completely():
    cache = PagedKVCacheManager(total_blocks=10, block_size_tokens=4)
    scheduler = ContinuousBatchScheduler(cache)
    scheduler.add_request("r1", 2, 2)
    
    scheduler.step()
    done = scheduler.step()
    assert done == ["r1"]
    assert len(scheduler.running_batch) == 0
    assert len(cache.free_blocks) == 10

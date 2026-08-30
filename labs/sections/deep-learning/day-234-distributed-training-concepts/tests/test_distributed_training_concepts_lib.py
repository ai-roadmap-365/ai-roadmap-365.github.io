import pytest
import numpy as np
from examples.distributed_training_concepts_lib import simulate_ring_allreduce, calculate_zero_sharding_memory

def test_ring_allreduce_exactness():
    t0 = np.array([1.0, 2.0, 3.0, 4.0])
    t1 = np.array([10.0, 20.0, 30.0, 40.0])
    res = simulate_ring_allreduce([t0, t1])
    expected = np.array([11.0, 22.0, 33.0, 44.0])
    np.testing.assert_allclose(res[0], expected)
    np.testing.assert_allclose(res[1], expected)

def test_ring_allreduce_4_ranks():
    tensors = [np.full(8, fill_value=float(i + 1)) for i in range(4)]
    res = simulate_ring_allreduce(tensors)
    # Sum of 1 + 2 + 3 + 4 = 10
    expected = np.full(8, 10.0)
    for r in range(4):
        np.testing.assert_allclose(res[r], expected)

def test_zero_memory_sharding():
    res = calculate_zero_sharding_memory(70.0, 64)
    assert res["ddp_per_gpu_gb"] == 1120.0
    assert res["zero3_fsdp_per_gpu_gb"] == 17.5
    assert res["zero1_per_gpu_gb"] < res["ddp_per_gpu_gb"]

import numpy as np
from typing import List, Dict, Any

def simulate_ring_allreduce(rank_tensors: List[np.ndarray]) -> List[np.ndarray]:
    P = len(rank_tensors)
    if P <= 1:
        return [t.copy() for t in rank_tensors]
    
    tensor_len = len(rank_tensors[0])
    chunk_size = tensor_len // P
    
    # Split into chunks per rank
    chunks = [[t[i*chunk_size:(i+1)*chunk_size].copy() for i in range(P)] for t in rank_tensors]
    
    # 1. Scatter-Reduce (P-1 steps)
    for step in range(P - 1):
        send_data = [chunks[r][(r - step) % P].copy() for r in range(P)]
        for r in range(P):
            recv_rank = (r + 1) % P
            recv_chunk_idx = (r - step) % P
            chunks[recv_rank][recv_chunk_idx] += send_data[r]
            
    # 2. All-Gather (P-1 steps)
    for step in range(P - 1):
        send_data = [chunks[r][(r - step + 1) % P].copy() for r in range(P)]
        for r in range(P):
            recv_rank = (r + 1) % P
            recv_chunk_idx = (r - step + 1) % P
            chunks[recv_rank][recv_chunk_idx] = send_data[r].copy()
            
    return [np.concatenate(chunks[r]) for r in range(P)]

def calculate_zero_sharding_memory(num_params_billions: float, num_gpus: int) -> Dict[str, float]:
    # In decimal GB (16 bytes per param static)
    # Params: 2B, Grads: 2B, Master: 4B, Mom1: 4B, Mom2: 4B -> Optim = 12B
    N = num_params_billions
    P = num_gpus

    ddp_gb = 16.0 * N
    zero1_gb = 4.0 * N + (12.0 * N) / P
    zero2_gb = 2.0 * N + (14.0 * N) / P
    zero3_gb = (16.0 * N) / P

    return {
        "num_params_billions": N,
        "num_gpus": P,
        "ddp_per_gpu_gb": round(ddp_gb, 2),
        "zero1_per_gpu_gb": round(zero1_gb, 2),
        "zero2_per_gpu_gb": round(zero2_gb, 2),
        "zero3_fsdp_per_gpu_gb": round(zero3_gb, 2)
    }

def run_distributed_demo():
    t0 = np.array([1.0, 1.0, 1.0, 1.0])
    t1 = np.array([2.0, 2.0, 2.0, 2.0])
    reduced = simulate_ring_allreduce([t0, t1])
    zero_mem = calculate_zero_sharding_memory(70.0, 64)

    print(f"Distributed Demo: Reduced Sum = {reduced[0].tolist()}, 70B on 64 GPUs ZeRO-3 = {zero_mem['zero3_fsdp_per_gpu_gb']} GB")
    return reduced, zero_mem

if __name__ == "__main__":
    run_distributed_demo()

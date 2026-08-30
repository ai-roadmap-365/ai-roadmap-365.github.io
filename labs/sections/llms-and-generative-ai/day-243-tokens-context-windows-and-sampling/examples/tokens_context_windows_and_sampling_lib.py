import torch
import torch.nn.functional as F
from typing import List, Optional

def calculate_kv_cache_bytes(
    batch_size: int,
    seq_len: int,
    num_layers: int,
    num_kv_heads: int,
    head_dim: int,
    bytes_per_elem: int = 2
) -> int:
    # 2 (Keys + Values) * Batch * SeqLen * NumLayers * (NumKVHeads * HeadDim) * BytesPerElem
    return 2 * batch_size * seq_len * num_layers * (num_kv_heads * head_dim) * bytes_per_elem

def sample_next_token(
    logits: torch.Tensor,
    temperature: float = 1.0,
    top_k: int = 0,
    top_p: float = 1.0
) -> int:
    logits = logits.clone().float()

    if temperature <= 1e-5:
        return int(torch.argmax(logits).item())

    logits = logits / temperature

    # Top-k filtering
    if top_k > 0:
        topk_vals, _ = torch.topk(logits, min(top_k, logits.shape[-1]))
        min_topk = topk_vals[-1]
        logits[logits < min_topk] = -float('inf')

    # Top-p filtering
    if 0.0 < top_p < 1.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

        sorted_indices_to_remove = cumulative_probs > top_p
        sorted_indices_to_remove[1:] = sorted_indices_to_remove[:-1].clone()
        sorted_indices_to_remove[0] = False

        indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = -float('inf')

    probs = F.softmax(logits, dim=-1)
    return int(torch.multinomial(probs, num_samples=1).item())

def run_sampling_demo():
    torch.manual_seed(42)
    # LLaMA-3-70B: 80 layers, 8 KV heads, head_dim 128, 8k context
    kv_bytes = calculate_kv_cache_bytes(1, 8192, 80, 8, 128, bytes_per_elem=2)
    kv_gb = kv_bytes / (1024**3)

    # Simulated vocabulary logits (vocab size 100)
    logits = torch.randn(100)
    logits[42] = 10.0 # Clear winner

    tok_greedy = sample_next_token(logits, temperature=0.0)
    tok_temp = sample_next_token(logits, temperature=0.7, top_p=0.9)

    print(f"Sampling Demo: KV Cache (8k context) = {kv_gb:.2f} GB, Greedy Token = {tok_greedy}, Sampled = {tok_temp}")
    return kv_gb, tok_greedy, tok_temp

if __name__ == "__main__":
    run_sampling_demo()

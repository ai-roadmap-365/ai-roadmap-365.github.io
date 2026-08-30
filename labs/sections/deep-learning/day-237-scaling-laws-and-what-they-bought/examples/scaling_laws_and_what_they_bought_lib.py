import math
from typing import Dict, Any

def calculate_training_flops(params_billions: float, tokens_billions: float) -> float:
    N = params_billions * 1e9
    D = tokens_billions * 1e9
    return 6.0 * N * D

def compute_chinchilla_optimal(compute_flops: float) -> Dict[str, Any]:
    # C = 6 * N * D = 6 * N * (20 * N) = 120 * N^2 -> N = sqrt(C / 120)
    N_opt = math.sqrt(compute_flops / 120.0)
    D_opt = 20.0 * N_opt

    # Chinchilla Loss constants
    E = 1.69
    A, alpha = 406.4, 0.34
    B, beta = 410.7, 0.28
    pred_loss = E + (A / (N_opt ** alpha)) + (B / (D_opt ** beta))

    return {
        "compute_flops": compute_flops,
        "optimal_params_billions": round(N_opt / 1e9, 2),
        "optimal_tokens_billions": round(D_opt / 1e9, 2),
        "predicted_loss": round(pred_loss, 4),
        "token_to_param_ratio": round(D_opt / N_opt, 1)
    }

def run_scaling_laws_demo():
    flops = calculate_training_flops(7.0, 140.0)
    alloc = compute_chinchilla_optimal(flops)

    print(f"Scaling Laws Demo: Compute = {flops:.2e} FLOPs, Optimal Params = {alloc['optimal_params_billions']}B, Tokens = {alloc['optimal_tokens_billions']}B")
    return flops, alloc

if __name__ == "__main__":
    run_scaling_laws_demo()

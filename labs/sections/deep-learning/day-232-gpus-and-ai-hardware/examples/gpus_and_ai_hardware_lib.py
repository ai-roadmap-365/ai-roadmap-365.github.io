import torch
from typing import Dict, Any

def compute_gemm_intensity(size: int, dtype_bytes: int = 2) -> Dict[str, Any]:
    total_flops = 2 * (size ** 3)
    total_bytes = 3 * (size ** 2) * dtype_bytes
    intensity = total_flops / total_bytes

    return {
        "size": size,
        "dtype_bytes": dtype_bytes,
        "total_flops": total_flops,
        "total_bytes": total_bytes,
        "arithmetic_intensity": round(intensity, 2)
    }

def calculate_machine_balance(peak_tflops: float, peak_bandwidth_tbs: float) -> float:
    # Peak FLOPs / Peak Bandwidth (TFLOPs / TB/s = FLOPs / Byte)
    return round(peak_tflops / peak_bandwidth_tbs, 2)

def run_hardware_demo():
    res_fp32 = compute_gemm_intensity(size=512, dtype_bytes=4)
    res_fp16 = compute_gemm_intensity(size=512, dtype_bytes=2)
    balance = calculate_machine_balance(peak_tflops=100.0, peak_bandwidth_tbs=0.8)

    print(f"Hardware Demo: FP16 Intensity = {res_fp16['arithmetic_intensity']} FLOPs/Byte, Balance = {balance}")
    return res_fp16, balance

if __name__ == "__main__":
    run_hardware_demo()

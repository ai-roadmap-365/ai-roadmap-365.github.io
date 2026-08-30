import pytest
from examples.gpus_and_ai_hardware_lib import compute_gemm_intensity, calculate_machine_balance

def test_gemm_intensity_fp16():
    res = compute_gemm_intensity(size=512, dtype_bytes=2)
    assert res["total_flops"] == 2 * (512 ** 3)
    assert res["total_bytes"] == 3 * (512 ** 2) * 2
    assert res["arithmetic_intensity"] == round((2 * 512) / 6, 2) # ~170.67

def test_gemm_intensity_fp32():
    res = compute_gemm_intensity(size=512, dtype_bytes=4)
    assert res["arithmetic_intensity"] == round((2 * 512) / 12, 2) # ~85.33

def test_machine_balance():
    balance = calculate_machine_balance(peak_tflops=1000.0, peak_bandwidth_tbs=3.35)
    assert balance == round(1000.0 / 3.35, 2)

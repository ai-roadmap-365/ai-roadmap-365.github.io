import pytest
from examples.mixed_precision_and_performance_lib import calculate_adamw_vram_gb, MockDynamicLossScaler

def test_adamw_vram_calculation():
    # 7 billion parameters: 16 bytes per param -> 112 GB (in decimal) ~ 104.3 GB (in binary GiB)
    res = calculate_adamw_vram_gb(7.0)
    assert res["total_static_vram_gb"] > 100.0
    assert res["master_weights_gb"] == 2 * res["model_weights_gb"]

def test_dynamic_loss_scaler_overflow():
    scaler = MockDynamicLossScaler(init_scale=65536.0, backoff_factor=0.5)
    assert scaler.step(has_overflow=False) == 65536.0
    assert scaler.step(has_overflow=True) == 32768.0

def test_dynamic_loss_scaler_growth():
    scaler = MockDynamicLossScaler(init_scale=1000.0, growth_factor=2.0, growth_interval=2)
    scaler.step(has_overflow=False)
    assert scaler.step(has_overflow=False) == 2000.0

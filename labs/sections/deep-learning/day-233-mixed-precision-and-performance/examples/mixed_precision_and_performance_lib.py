from typing import Dict, Any

def calculate_adamw_vram_gb(num_params_billions: float) -> Dict[str, float]:
    params = num_params_billions * 1e9
    
    fp16_params_gb = (params * 2) / (1024 ** 3)
    fp16_grads_gb = (params * 2) / (1024 ** 3)
    fp32_master_gb = (params * 4) / (1024 ** 3)
    fp32_mom1_gb = (params * 4) / (1024 ** 3)
    fp32_mom2_gb = (params * 4) / (1024 ** 3)

    total_static_gb = fp16_params_gb + fp16_grads_gb + fp32_master_gb + fp32_mom1_gb + fp32_mom2_gb

    return {
        "params_billions": num_params_billions,
        "model_weights_gb": round(fp16_params_gb, 2),
        "gradients_gb": round(fp16_grads_gb, 2),
        "master_weights_gb": round(fp32_master_gb, 2),
        "optimizer_moments_gb": round(fp32_mom1_gb + fp32_mom2_gb, 2),
        "total_static_vram_gb": round(total_static_gb, 2)
    }

class MockDynamicLossScaler:
    def __init__(self, init_scale: float = 65536.0, growth_factor: float = 2.0,
                 backoff_factor: float = 0.5, growth_interval: int = 2000):
        self.scale = init_scale
        self.growth_factor = growth_factor
        self.backoff_factor = backoff_factor
        self.growth_interval = growth_interval
        self.successful_steps = 0

    def step(self, has_overflow: bool) -> float:
        if has_overflow:
            self.scale *= self.backoff_factor
            self.successful_steps = 0
        else:
            self.successful_steps += 1
            if self.successful_steps >= self.growth_interval:
                self.scale *= self.growth_factor
                self.successful_steps = 0
        return self.scale

def run_mixed_precision_demo():
    vram = calculate_adamw_vram_gb(7.0)
    scaler = MockDynamicLossScaler(init_scale=65536.0)
    s1 = scaler.step(has_overflow=False)
    s2 = scaler.step(has_overflow=True)

    print(f"Mixed Precision Demo: 7B Model Static VRAM = {vram['total_static_vram_gb']} GB, Scale after overflow = {s2}")
    return vram, s2

if __name__ == "__main__":
    run_mixed_precision_demo()

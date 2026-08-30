# Starter: Diffusion Noise Scheduler
import numpy as np
from typing import Tuple, Optional

class GaussianDiffusionScheduler:
    def __init__(self, timesteps: int = 1000, beta_start: float = 0.0001, beta_end: float = 0.02, schedule_type: str = "linear"):
        self.timesteps = timesteps
        self.betas = np.linspace(beta_start, beta_end, timesteps, dtype=np.float32)
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = np.cumprod(self.alphas)

    def add_noise(self, original_samples: np.ndarray, noise: np.ndarray, timesteps: np.ndarray) -> np.ndarray:
        return original_samples + noise

    def step_denoise(self, model_output_noise: np.ndarray, timestep: int, sample: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        return sample - model_output_noise

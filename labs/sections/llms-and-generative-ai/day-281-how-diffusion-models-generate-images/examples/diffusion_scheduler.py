# Gaussian Diffusion Noise Scheduler and Reverse Denoising Simulator
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

class GaussianDiffusionScheduler:
    """Vectorized Gaussian Diffusion Noise Scheduler supporting Linear and Cosine schedules."""

    def __init__(self, timesteps: int = 1000, beta_start: float = 0.0001, beta_end: float = 0.02, schedule_type: str = "linear"):
        self.timesteps = timesteps
        self.schedule_type = schedule_type

        if schedule_type == "linear":
            self.betas = np.linspace(beta_start, beta_end, timesteps, dtype=np.float32)
        elif schedule_type == "cosine":
            # Nichol & Dhariwal cosine schedule
            steps = timesteps + 1
            s = 0.008
            x = np.linspace(0, timesteps, steps, dtype=np.float32)
            alphas_cumprod = np.cos(((x / timesteps) + s) / (1 + s) * np.pi * 0.5) ** 2
            alphas_cumprod = alphas_cumprod / alphas_cumprod[0]
            betas = 1.0 - (alphas_cumprod[1:] / alphas_cumprod[:-1])
            self.betas = np.clip(betas, a_min=0.0, a_max=0.999).astype(np.float32)
        else:
            raise ValueError(f"Unknown schedule type: {schedule_type}")

        self.alphas = (1.0 - self.betas).astype(np.float32)
        self.alphas_cumprod = np.cumprod(self.alphas, axis=0).astype(np.float32)
        self.alphas_cumprod_prev = np.append(1.0, self.alphas_cumprod[:-1]).astype(np.float32)

    def add_noise(self, original_samples: np.ndarray, noise: np.ndarray, timesteps: np.ndarray) -> np.ndarray:
        """
        Vectorized forward noise injection: x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * noise
        original_samples: (B, C, H, W) or (B, N)
        noise: (B, C, H, W)
        timesteps: (B,)
        """
        sqrt_alpha_prod = np.sqrt(self.alphas_cumprod[timesteps])
        sqrt_one_minus_alpha_prod = np.sqrt(1.0 - self.alphas_cumprod[timesteps])

        # Match dimensions for broadcasting
        while sqrt_alpha_prod.ndim < original_samples.ndim:
            sqrt_alpha_prod = np.expand_dims(sqrt_alpha_prod, axis=-1)
            sqrt_one_minus_alpha_prod = np.expand_dims(sqrt_one_minus_alpha_prod, axis=-1)

        return (sqrt_alpha_prod * original_samples + sqrt_one_minus_alpha_prod * noise).astype(np.float32)

    def step_denoise(self, model_output_noise: np.ndarray, timestep: int, sample: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        """
        Executes single reverse step: p(x_{t-1} | x_t)
        """
        if timestep < 0 or timestep >= self.timesteps:
            raise ValueError(f"Timestep {timestep} out of bounds [0, {self.timesteps - 1}]")

        alpha = self.alphas[timestep]
        alpha_cumprod = self.alphas_cumprod[timestep]
        beta = self.betas[timestep]

        # Compute predicted previous sample mean mu_t
        pred_prev_sample = (1.0 / np.sqrt(alpha)) * (
            sample - (beta / np.sqrt(1.0 - alpha_cumprod)) * model_output_noise
        )

        if timestep > 0:
            if seed is not None:
                np.random.seed(seed)
            noise = np.random.randn(*sample.shape).astype(np.float32)
            variance = np.sqrt(beta) * noise
            pred_prev_sample = pred_prev_sample + variance

        return pred_prev_sample.astype(np.float32)

    def sample_loop(self, model_fn, shape: Tuple[int, ...], seed: int = 42) -> np.ndarray:
        """Simulates complete reverse sampling trajectory from pure noise to clean sample."""
        np.random.seed(seed)
        current_sample = np.random.randn(*shape).astype(np.float32)

        for t in reversed(range(self.timesteps)):
            pred_noise = model_fn(current_sample, t)
            current_sample = self.step_denoise(pred_noise, t, current_sample, seed=seed + t)

        return current_sample

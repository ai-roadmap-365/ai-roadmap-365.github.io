# Starter: Latent Diffusion Pipeline Simulator
import numpy as np
from typing import Dict, Tuple

class LatentDiffusionPipelineSimulator:
    def __init__(self, vae_scale_factor: float = 0.18215):
        self.vae_scale_factor = vae_scale_factor

    @staticmethod
    def compute_cfg_noise(uncond_noise: np.ndarray, cond_noise: np.ndarray, guidance_scale: float) -> np.ndarray:
        return cond_noise

    def encode_pixels_to_latents(self, rgb_image: np.ndarray) -> np.ndarray:
        return np.zeros((1, 4, 8, 8), dtype=np.float32)

    def decode_latents_to_pixels(self, latents: np.ndarray) -> np.ndarray:
        return np.zeros((1, 3, 64, 64), dtype=np.uint8)

# Latent Diffusion Pipeline and Classifier-Free Guidance Simulator
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

class LatentDiffusionPipelineSimulator:
    """Simulates Latent Diffusion inference, CFG extrapolation, and VAE decoding."""

    def __init__(self, vae_scale_factor: float = 0.18215):
        self.vae_scale_factor = vae_scale_factor

    @staticmethod
    def compute_cfg_noise(uncond_noise: np.ndarray, cond_noise: np.ndarray, guidance_scale: float) -> np.ndarray:
        """
        Calculates guided noise: eps = uncond + s * (cond - uncond)
        """
        if uncond_noise.shape != cond_noise.shape:
            raise ValueError(f"Shape mismatch: uncond {uncond_noise.shape} vs cond {cond_noise.shape}")
        
        delta = cond_noise - uncond_noise
        guided_noise = uncond_noise + float(guidance_scale) * delta
        return guided_noise.astype(np.float32)

    @staticmethod
    def compute_negative_prompt_cfg(neg_noise: np.ndarray, pos_noise: np.ndarray, guidance_scale: float) -> np.ndarray:
        """
        Applies negative prompt steering by substituting neg_noise as the baseline.
        """
        return LatentDiffusionPipelineSimulator.compute_cfg_noise(neg_noise, pos_noise, guidance_scale)

    def encode_pixels_to_latents(self, rgb_image: np.ndarray) -> np.ndarray:
        """
        Simulates 8x VAE spatial downsampling from RGB (B, 3, H, W) to Latents (B, 4, H//8, W//8).
        """
        # Normalize RGB [0, 255] to [-1, 1]
        normalized = (rgb_image.astype(np.float32) / 127.5) - 1.0
        # Average 8x8 spatial patches and add 4th dummy latent channel
        b, c, h, w = normalized.shape
        downsampled = normalized[:, :, ::8, ::8]
        # Pad to 4 channels
        dummy_channel = np.mean(downsampled, axis=1, keepdims=True) * 0.5
        latents = np.concatenate([downsampled, dummy_channel], axis=1) * self.vae_scale_factor
        return latents.astype(np.float32)

    def decode_latents_to_pixels(self, latents: np.ndarray) -> np.ndarray:
        """
        Simulates 8x VAE spatial upsampling from Latents (B, 4, H, W) to RGB (B, 3, H*8, W*8).
        """
        unscaled = latents[:, :3, :, :] / self.vae_scale_factor
        upsampled = np.repeat(np.repeat(unscaled, 8, axis=2), 8, axis=3)
        rgb = np.clip((upsampled + 1.0) * 127.5, 0.0, 255.0).astype(np.uint8)
        return rgb

    def evaluate_compression_metrics(self, rgb_shape: Tuple[int, ...], latent_shape: Tuple[int, ...]) -> Dict[str, float]:
        """Calculates numerical compression factor of latent space."""
        rgb_elements = float(np.prod(rgb_shape))
        latent_elements = float(np.prod(latent_shape))
        ratio = rgb_elements / latent_elements if latent_elements > 0 else 1.0
        savings = (1.0 - (latent_elements / rgb_elements)) * 100.0 if rgb_elements > 0 else 0.0
        
        return {
            "rgb_elements": rgb_elements,
            "latent_elements": latent_elements,
            "compression_factor": ratio,
            "savings_percentage": savings
        }

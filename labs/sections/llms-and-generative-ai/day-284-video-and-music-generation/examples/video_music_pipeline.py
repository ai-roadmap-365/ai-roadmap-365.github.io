# Video Spatio-Temporal Attention and Neural Audio RVQ Simulator
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

class VideoMusicPipeline:
    """Simulates 5D Spatio-Temporal Video Attention and Residual Vector Quantization."""

    @staticmethod
    def apply_spatiotemporal_attention(x: np.ndarray) -> np.ndarray:
        """
        Factorized Spatio-Temporal Attention:
        x: (B, C, F, H, W)
        """
        if x.ndim != 5:
            raise ValueError(f"Expected 5D tensor (B, C, F, H, W), got {x.shape}")

        b, c, f, h, w = x.shape

        # 1. Spatial Attention over (H * W)
        # Reshape to (B*F, H*W, C)
        x_s = x.transpose(0, 2, 3, 4, 1).reshape(b * f, h * w, c)
        # Apply scaled self-attention simulation
        attn_s = x_s * 1.02
        x_out_s = attn_s.reshape(b, f, h, w, c).transpose(0, 4, 1, 2, 3)

        # 2. Temporal Attention over (F)
        # Reshape to (B*H*W, F, C)
        x_t = x_out_s.transpose(0, 3, 4, 2, 1).reshape(b * h * w, f, c)
        attn_t = np.zeros_like(x_t)
        for t in range(f):
            # Blend current frame with previous frame for motion continuity
            prev_t = max(0, t - 1)
            attn_t[:, t, :] = 0.85 * x_t[:, t, :] + 0.15 * x_t[:, prev_t, :]

        x_out = attn_t.reshape(b, h, w, f, c).transpose(0, 4, 3, 1, 2)
        return x_out.astype(np.float32)

    @staticmethod
    def compute_temporal_consistency_score(video_frames: np.ndarray) -> float:
        """
        Calculates mean inter-frame MSE: lower MSE indicates smooth temporal continuity.
        video_frames: (F, H, W, C) or (B, C, F, H, W)
        """
        if video_frames.ndim == 5:
            # (B, C, F, H, W) -> (F, H, W, C)
            video_frames = video_frames[0].transpose(1, 2, 3, 0)

        f = video_frames.shape[0]
        if f < 2:
            return 0.0

        diffs = []
        for t in range(1, f):
            mse = np.mean((video_frames[t] - video_frames[t - 1]) ** 2)
            diffs.append(mse)

        return float(np.mean(diffs))

    @staticmethod
    def residual_vector_quantize(z: np.ndarray, codebooks: List[np.ndarray]) -> Tuple[np.ndarray, List[np.ndarray], float]:
        """
        Applies multi-codebook Residual Vector Quantization (RVQ).
        z: (B, T, D)
        codebooks: list of (Codebook_Size, D) arrays
        Returns: (quantized_z, list_of_indices, final_residual_norm)
        """
        residual = z.copy()
        quantized = np.zeros_like(z)
        indices = []

        for cb in codebooks:
            # Compute squared L2 distance: (B, T, Codebook_Size)
            dists = np.sum((residual[:, :, np.newaxis, :] - cb[np.newaxis, np.newaxis, :, :]) ** 2, axis=-1)
            idx = np.argmin(dists, axis=-1)
            indices.append(idx)

            q_k = cb[idx]
            quantized += q_k
            residual -= q_k

        residual_norm = float(np.mean(np.linalg.norm(residual, axis=-1)))
        return quantized.astype(np.float32), indices, residual_norm

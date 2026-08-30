import pytest
import numpy as np
from video_music_pipeline import VideoMusicPipeline

def test_spatiotemporal_tensor_shape():
    # Batch 2, Channels 4, Frames 8, Height 16, Width 16
    x = np.random.randn(2, 4, 8, 16, 16).astype(np.float32)
    out = VideoMusicPipeline.apply_spatiotemporal_attention(x)
    
    assert out.shape == (2, 4, 8, 16, 16)
    assert not np.isnan(out).any()

def test_temporal_attention_smoothing():
    # Verify temporal attention reduces abrupt frame differences
    x = np.zeros((1, 1, 4, 2, 2), dtype=np.float32)
    # Inject spike at frame 2
    x[0, 0, 2, :, :] = 10.0
    
    out = VideoMusicPipeline.apply_spatiotemporal_attention(x)
    # Frame 2 should be tempered and frame 3 should receive residual temporal blend
    assert out[0, 0, 2, 0, 0] < 10.0
    assert out[0, 0, 3, 0, 0] > 0.0

def test_temporal_consistency_score():
    frames = np.ones((5, 10, 10, 3), dtype=np.float32)
    # Identical frames have 0.0 variance
    assert VideoMusicPipeline.compute_temporal_consistency_score(frames) == 0.0
    
    # Add noise
    frames[1] += 2.0
    score = VideoMusicPipeline.compute_temporal_consistency_score(frames)
    assert score > 0.0

def test_rvq_quantization_convergence():
    np.random.seed(42)
    z = np.random.randn(2, 10, 16).astype(np.float32)
    
    # 3 Codebooks with 64 vectors each
    codebooks = [np.random.randn(64, 16).astype(np.float32) for _ in range(3)]
    
    quantized, indices, residual_norm = VideoMusicPipeline.residual_vector_quantize(z, codebooks)
    
    assert quantized.shape == z.shape
    assert len(indices) == 3
    assert indices[0].shape == (2, 10)
    # Quantization error should be lower than raw input norm
    raw_norm = float(np.mean(np.linalg.norm(z, axis=-1)))
    assert residual_norm < raw_norm

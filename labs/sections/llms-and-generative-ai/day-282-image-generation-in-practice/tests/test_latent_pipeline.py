import pytest
import numpy as np
from latent_pipeline import LatentDiffusionPipelineSimulator

@pytest.fixture
def pipeline():
    return LatentDiffusionPipelineSimulator(vae_scale_factor=0.18215)

def test_cfg_extrapolation_math(pipeline):
    uncond = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    cond = np.array([[1.5, 3.0], [3.5, 5.0]], dtype=np.float32)
    
    # delta = cond - uncond = [[0.5, 1.0], [0.5, 1.0]]
    # scale = 7.0 -> guided = uncond + 7.0 * delta
    guided = pipeline.compute_cfg_noise(uncond, cond, guidance_scale=7.0)
    
    expected = uncond + 7.0 * (cond - uncond)
    assert np.allclose(guided, expected)
    assert guided[0, 0] == 1.0 + 7.0 * 0.5 # 4.5

def test_cfg_scale_one_passthrough(pipeline):
    uncond = np.random.randn(2, 4, 8, 8).astype(np.float32)
    cond = np.random.randn(2, 4, 8, 8).astype(np.float32)
    
    # Scale 1.0 returns cond exactly
    guided = pipeline.compute_cfg_noise(uncond, cond, guidance_scale=1.0)
    assert np.allclose(guided, cond)

def test_negative_prompt_steering(pipeline):
    neg = np.array([[-1.0, -1.0]], dtype=np.float32)
    pos = np.array([[1.0, 1.0]], dtype=np.float32)
    
    guided = pipeline.compute_negative_prompt_cfg(neg, pos, guidance_scale=5.0)
    # delta = 2.0 -> -1.0 + 5.0 * 2.0 = 9.0
    assert np.allclose(guided, np.array([[9.0, 9.0]]))

def test_vae_roundtrip_dimensions(pipeline):
    rgb = np.random.randint(0, 256, (2, 3, 64, 64), dtype=np.uint8)
    latents = pipeline.encode_pixels_to_latents(rgb)
    
    assert latents.shape == (2, 4, 8, 8) # 8x spatial downsampling, 4 channels
    
    recon_rgb = pipeline.decode_latents_to_pixels(latents)
    assert recon_rgb.shape == (2, 3, 64, 64)
    assert recon_rgb.dtype == np.uint8

def test_compression_metrics(pipeline):
    metrics = pipeline.evaluate_compression_metrics((1, 3, 512, 512), (1, 4, 64, 64))
    assert metrics["rgb_elements"] == 1 * 3 * 512 * 512 # 786,432
    assert metrics["latent_elements"] == 1 * 4 * 64 * 64 # 16,384
    assert metrics["compression_factor"] == 48.0 # 48x reduction
    assert metrics["savings_percentage"] > 97.0

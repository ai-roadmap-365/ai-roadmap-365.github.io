import pytest
import numpy as np
from diffusion_scheduler import GaussianDiffusionScheduler

@pytest.fixture
def linear_scheduler():
    return GaussianDiffusionScheduler(timesteps=100, beta_start=0.0001, beta_end=0.02, schedule_type="linear")

@pytest.fixture
def cosine_scheduler():
    return GaussianDiffusionScheduler(timesteps=100, schedule_type="cosine")

def test_schedule_properties(linear_scheduler, cosine_scheduler):
    assert len(linear_scheduler.betas) == 100
    assert linear_scheduler.alphas_cumprod[0] > linear_scheduler.alphas_cumprod[-1]
    assert np.all(linear_scheduler.betas > 0.0)
    assert np.all(linear_scheduler.betas < 1.0)

    # Cosine schedule starts near 1.0 and smoothly decays
    assert cosine_scheduler.alphas_cumprod[0] > 0.99
    assert cosine_scheduler.alphas_cumprod[-1] < 0.01

def test_forward_diffusion_closed_form(linear_scheduler):
    np.random.seed(42)
    x0 = np.ones((4, 3, 16, 16), dtype=np.float32)
    noise = np.random.randn(4, 3, 16, 16).astype(np.float32)
    t = np.array([0, 25, 50, 99], dtype=np.int64)

    xt = linear_scheduler.add_noise(x0, noise, t)
    assert xt.shape == (4, 3, 16, 16)
    
    # At t=0, alpha_cumprod ~ 0.9999 -> xt is almost pure x0
    assert np.mean(np.abs(xt[0] - x0[0])) < 0.1
    # At t=99, xt is dominated by noise
    assert np.std(xt[3]) > 0.7

def test_reverse_step_denoise(linear_scheduler):
    np.random.seed(42)
    sample = np.random.randn(2, 4).astype(np.float32)
    pred_noise = np.zeros_like(sample)
    
    prev_sample = linear_scheduler.step_denoise(pred_noise, timestep=50, sample=sample, seed=42)
    assert prev_sample.shape == sample.shape
    assert not np.isnan(prev_sample).any()

def test_timestep_bounds(linear_scheduler):
    sample = np.zeros((2, 2), dtype=np.float32)
    with pytest.raises(ValueError, match="out of bounds"):
        linear_scheduler.step_denoise(sample, timestep=100, sample=sample)

def test_sample_loop_reconstruction():
    scheduler = GaussianDiffusionScheduler(timesteps=10, schedule_type="linear")
    
    # Mock model function that returns scaled current noise
    def mock_model(x, t):
        return x * 0.1
        
    final_sample = scheduler.sample_loop(mock_model, shape=(2, 8), seed=42)
    assert final_sample.shape == (2, 8)
    assert not np.isnan(final_sample).any()

import pytest
import numpy as np
from multimodal_app import MultimodalApplicationOrchestrator

@pytest.fixture
def orchestrator():
    return MultimodalApplicationOrchestrator(vae_scale=0.18215, default_guidance_scale=7.5)

def test_speech_ingestion_and_transcription(orchestrator):
    vocab = ["<blank>", "d", "e", "s", "i", "g", "n", " "]
    waveform = np.ones(3200, dtype=np.float32) * 0.05
    
    transcript = orchestrator.transcribe_audio_waveform(waveform, vocab)
    assert isinstance(transcript, str)

def test_visual_feature_projection(orchestrator):
    img = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    features = orchestrator.project_visual_features(img, target_dim=64)
    
    assert features.shape == (64,)
    assert not np.isnan(features).any()

def test_latent_diffusion_image_synthesis(orchestrator):
    img = orchestrator.synthesize_image("modern villa", guidance_scale=7.5)
    
    assert img.shape == (128, 128, 3) # 16x16 latents * 8 upsampling = 128x128 RGB
    assert img.dtype == np.uint8

def test_c2pa_provenance_signing_and_verification(orchestrator):
    img = np.zeros((32, 32, 3), dtype=np.uint8)
    provenance = orchestrator.sign_and_verify_provenance(img, author="TestArchitect")
    
    assert provenance["is_valid"] is True
    assert provenance["manifest"]["author"] == "TestArchitect"
    assert len(provenance["payload_hash"]) == 64

def test_end_to_end_multimodal_pipeline(orchestrator):
    vocab = ["<blank>", "a", "b", "c", " "]
    audio = np.random.randn(1600).astype(np.float32)
    img = np.random.randint(0, 256, (32, 32, 3), dtype=np.uint8)
    
    result = orchestrator.run_full_pipeline(audio, img, vocab)
    assert result["status"] == "SUCCESS"
    assert result["provenance"]["is_valid"] is True
    assert result["generated_image_shape"] == (128, 128, 3)

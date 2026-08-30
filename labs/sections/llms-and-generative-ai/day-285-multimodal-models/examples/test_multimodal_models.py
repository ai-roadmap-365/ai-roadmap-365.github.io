import pytest
import numpy as np
from multimodal_models import MultimodalPipeline

def test_clip_infonce_perfect_alignment():
    # When image and text embeddings are identical, loss should be minimal
    emb = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    loss, logits = MultimodalPipeline.compute_clip_infonce_loss(emb, emb, temperature=0.1)
    
    assert loss < 0.1
    assert logits[0, 0] > logits[0, 1] # Diagonal similarity is maximized

def test_clip_infonce_symmetry():
    np.random.seed(42)
    img = np.random.randn(4, 8).astype(np.float32)
    txt = np.random.randn(4, 8).astype(np.float32)
    
    loss, logits = MultimodalPipeline.compute_clip_infonce_loss(img, txt, temperature=0.07)
    assert not np.isnan(loss)
    assert logits.shape == (4, 4)

def test_zero_shot_classification():
    img = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    class_txt = np.array([
        [1.0, 0.0, 0.0], # Target class: 'cat'
        [0.0, 1.0, 0.0], # 'dog'
        [0.0, 0.0, 1.0], # 'car'
    ], dtype=np.float32)
    labels = ["cat", "dog", "car"]
    
    result = MultimodalPipeline.zero_shot_classify(img, class_txt, labels)
    assert result["predicted_label"] == "cat"
    assert result["confidence"] > 0.5
    assert result["probabilities"]["dog"] < 0.3

def test_mlp_projector_transformation():
    # 2 visual tokens, vision_dim=4, llm_dim=8
    tokens = np.random.randn(1, 2, 4).astype(np.float32)
    w1 = np.random.randn(4, 8).astype(np.float32) * 0.1
    b1 = np.zeros(8, dtype=np.float32)
    w2 = np.random.randn(8, 8).astype(np.float32) * 0.1
    b2 = np.zeros(8, dtype=np.float32)
    
    projected = MultimodalPipeline.project_visual_tokens(tokens, w1, b1, w2, b2)
    assert projected.shape == (1, 2, 8)
    assert not np.isnan(projected).any()

def test_visual_token_counter():
    assert MultimodalPipeline.calculate_visual_token_count(336, patch_size=14) == 576
    assert MultimodalPipeline.calculate_visual_token_count(224, patch_size=14) == 256

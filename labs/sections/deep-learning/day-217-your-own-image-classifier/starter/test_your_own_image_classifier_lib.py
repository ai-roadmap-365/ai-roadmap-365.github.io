import pytest
import torch
import numpy as np
from examples.your_own_image_classifier_lib import calculate_simple_phash, hamming_distance, generate_error_gallery

def test_phash_identical_images():
    img = np.ones((16, 16), dtype=np.float32)
    h1 = calculate_simple_phash(img)
    h2 = calculate_simple_phash(img)
    assert hamming_distance(h1, h2) == 0

def test_error_gallery_high_confidence_sorting():
    logits = torch.tensor([
        [4.0, 0.1], # pred 0, true 0 (correct)
        [0.1, 2.0], # pred 1, true 0 (error, conf ~87%)
        [0.1, 5.0]  # pred 1, true 0 (error, conf ~99%)
    ])
    targets = torch.tensor([0, 0, 0])
    class_names = ["Cat", "Dog"]

    gallery = generate_error_gallery(logits, targets, class_names, top_n=2)
    assert len(gallery) == 2
    # First failure must be sample 2 (confidence ~99%)
    assert gallery[0]["sample_idx"] == 2
    assert gallery[1]["sample_idx"] == 1

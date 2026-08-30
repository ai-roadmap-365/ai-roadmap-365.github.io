import pytest
import numpy as np
import torch
import torch.nn.functional as F
from examples.convolutions_lib import calculate_conv_output_dim, custom_conv2d_numpy

def test_calculate_conv_output_dim():
    # 32x32 with K=3, S=1, P=1 -> 32x32
    assert calculate_conv_output_dim(32, 32, 3, stride=1, padding=1) == (32, 32)
    # 32x32 with K=3, S=2, P=1 -> 16x16
    assert calculate_conv_output_dim(32, 32, 3, stride=2, padding=1) == (16, 16)
    # 32x32 with K=5, S=1, P=0 -> 28x28
    assert calculate_conv_output_dim(32, 32, 5, stride=1, padding=0) == (28, 28)

def test_custom_conv2d_numpy_matches_pytorch():
    np.random.seed(42)
    x = np.random.randn(2, 3, 8, 8).astype(np.float32)
    w = np.random.randn(4, 3, 3, 3).astype(np.float32)
    b = np.random.randn(4).astype(np.float32)

    out_np = custom_conv2d_numpy(x, w, b, stride=1, padding=1)

    x_t = torch.from_numpy(x)
    w_t = torch.from_numpy(w)
    b_t = torch.from_numpy(b)
    out_pt = F.conv2d(x_t, w_t, b_t, stride=1, padding=1).numpy()

    assert np.allclose(out_np, out_pt, atol=1e-5)

def test_sobel_edge_detection_filter():
    sobel_v = np.array([
        [-1.0, 0.0, 1.0],
        [-2.0, 0.0, 2.0],
        [-1.0, 0.0, 1.0]
    ], dtype=np.float32).reshape(1, 1, 3, 3)

    img = np.zeros((1, 1, 6, 6), dtype=np.float32)
    img[:, :, :, 3:] = 1.0 # Vertical edge at col 3

    out = custom_conv2d_numpy(img, sobel_v, padding=1)
    # At column 2 and 3, horizontal gradient should be non-zero
    assert out[0, 0, 2, 2] != 0.0 or out[0, 0, 2, 3] != 0.0

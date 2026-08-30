import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Dict, Any

def calculate_conv_output_dim(h_in: int, w_in: int, k: int,
                              stride: int = 1, padding: int = 0) -> Tuple[int, int]:
    h_out = ((h_in - k + 2 * padding) // stride) + 1
    w_out = ((w_in - k + 2 * padding) // stride) + 1
    return h_out, w_out

def custom_conv2d_numpy(x: np.ndarray, weight: np.ndarray, bias: np.ndarray = None,
                         stride: int = 1, padding: int = 0) -> np.ndarray:
    # x shape: (N, C_in, H, W)
    # weight shape: (C_out, C_in, K_h, K_w)
    N, C_in, H, W = x.shape
    C_out, _, K_h, K_w = weight.shape

    H_out, W_out = calculate_conv_output_dim(H, W, K_h, stride, padding)

    # Pad input
    if padding > 0:
        x_padded = np.pad(x, ((0, 0), (0, 0), (padding, padding), (padding, padding)), mode='constant')
    else:
        x_padded = x

    out = np.zeros((N, C_out, H_out, W_out), dtype=np.float32)

    for n in range(N):
        for c_out in range(C_out):
            for i in range(H_out):
                h_start = i * stride
                h_end = h_start + K_h
                for j in range(W_out):
                    w_start = j * stride
                    w_end = w_start + K_w
                    patch = x_padded[n, :, h_start:h_end, w_start:w_end]
                    val = np.sum(patch * weight[c_out])
                    if bias is not None:
                        val += bias[c_out]
                    out[n, c_out, i, j] = val

    return out

def run_conv_demo():
    np.random.seed(42)
    x = np.random.randn(2, 3, 16, 16).astype(np.float32)
    w = np.random.randn(4, 3, 3, 3).astype(np.float32)
    b = np.random.randn(4).astype(np.float32)

    out_np = custom_conv2d_numpy(x, w, b, stride=1, padding=1)

    # Compare with PyTorch
    x_t = torch.from_numpy(x)
    w_t = torch.from_numpy(w)
    b_t = torch.from_numpy(b)
    out_pt = F.conv2d(x_t, w_t, b_t, stride=1, padding=1).numpy()

    max_diff = float(np.max(np.abs(out_np - out_pt)))
    print(f"2D Conv Demo: Output Shape = {out_np.shape}, Max Diff vs PyTorch = {max_diff:.6e}")
    return out_np.shape, max_diff

if __name__ == "__main__":
    run_conv_demo()

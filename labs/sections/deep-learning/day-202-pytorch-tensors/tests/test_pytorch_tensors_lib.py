import pytest
import numpy as np
from examples.pytorch_tensors_lib import PyTorchTensorToolkit

def test_tensor_strides_and_contiguity():
    arr = np.arange(24).reshape(2, 3, 4)
    info = PyTorchTensorToolkit.tensor_strides_demo(arr)

    assert info["orig_shape"] == (2, 3, 4)
    assert info["orig_contiguous"] is True
    assert info["transposed_contiguous"] is False
    assert info["flattened_shape"] == (24,)

def test_linear_autograd_gradients_accuracy():
    np.random.seed(42)
    m = 5
    in_dim = 3
    out_dim = 2

    X = np.random.randn(in_dim, m)
    W = np.random.randn(out_dim, in_dim)
    b = np.random.randn(out_dim, 1)

    Z, dW, db = PyTorchTensorToolkit.linear_autograd_simulation(X, W, b)

    assert Z.shape == (out_dim, m)
    assert dW.shape == (out_dim, in_dim)
    assert db.shape == (out_dim, 1)

def test_numerical_gradient_verification():
    X = np.array([[1.0, 2.0]], dtype=float).T # (2, 1)
    W = np.array([[2.0, 3.0]], dtype=float)    # (1, 2)
    b = np.array([[1.0]], dtype=float)         # (1, 1)

    Z, dW_ana, db_ana = PyTorchTensorToolkit.linear_autograd_simulation(X, W, b)

    # Numerical gradient check on W
    eps = 1e-5
    dW_num = np.zeros_like(W)
    for i in range(W.shape[0]):
        for j in range(W.shape[1]):
            orig = W[i, j]
            W[i, j] = orig + eps
            loss_p = np.sum((np.dot(W, X) + b) ** 2)
            W[i, j] = orig - eps
            loss_m = np.sum((np.dot(W, X) + b) ** 2)
            W[i, j] = orig
            dW_num[i, j] = (loss_p - loss_m) / (2.0 * eps)

    rel_err = np.linalg.norm(dW_ana - dW_num) / (np.linalg.norm(dW_ana) + 1e-8)
    assert rel_err < 1e-6

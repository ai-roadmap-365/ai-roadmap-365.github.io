import pytest
import numpy as np
from examples.backpropagation_lib import BackpropEngine, gradient_check_layer

def test_linear_and_relu_backward():
    m = 4
    A_prev = np.random.randn(5, m)
    W = np.random.randn(3, 5) * 0.1
    b = np.zeros((3, 1))
    Z = np.dot(W, A_prev) + b
    dA = np.random.randn(3, m)

    dZ = BackpropEngine.relu_backward(dA, Z)
    assert dZ.shape == (3, m)
    # Check that where Z <= 0, dZ is strictly 0.0
    assert np.all(dZ[Z <= 0.0] == 0.0)

    cache = {"A_prev": A_prev, "W": W, "b": b, "Z": Z}
    dA_prev, dW, db = BackpropEngine.linear_backward(dZ, cache)
    assert dW.shape == (3, 5)
    assert db.shape == (3, 1)
    assert dA_prev.shape == (5, m)

def test_full_backpropagation_gradient_shapes():
    m = 8
    X = np.random.randn(6, m)
    Y = np.zeros((2, m))
    Y[0, :] = 1.0

    W1 = np.random.randn(4, 6) * 0.1
    b1 = np.zeros((4, 1))
    Z1 = np.dot(W1, X) + b1
    A1 = np.maximum(0.0, Z1)

    W2 = np.random.randn(2, 4) * 0.1
    b2 = np.zeros((2, 1))
    Z2 = np.dot(W2, A1) + b2
    exp_Z2 = np.exp(Z2 - np.max(Z2, axis=0, keepdims=True))
    A2 = exp_Z2 / np.sum(exp_Z2, axis=0, keepdims=True)

    caches = [
        {"A_prev": X, "Z": Z1, "W": W1, "b": b1},
        {"A_prev": A1, "Z": Z2, "W": W2, "b": b2}
    ]
    grads = BackpropEngine.full_backward_pass(A2, Y, caches, ["relu", "softmax"])

    assert grads["dW1"].shape == (4, 6)
    assert grads["db1"].shape == (4, 1)
    assert grads["dW2"].shape == (2, 4)
    assert grads["db2"].shape == (2, 1)

def test_numerical_gradient_check():
    np.random.seed(123)
    m = 10
    X = np.random.randn(4, m)
    Y = np.zeros((2, m))
    Y[0, :] = 1.0

    W = np.random.randn(2, 4) * 0.1
    b = np.zeros((2, 1))
    Z = np.dot(W, X) + b
    exp_Z = np.exp(Z - np.max(Z, axis=0, keepdims=True))
    A = exp_Z / np.sum(exp_Z, axis=0, keepdims=True)

    cache = {"A_prev": X, "Z": Z, "W": W, "b": b}
    grads = BackpropEngine.full_backward_pass(A, Y, [cache], ["softmax"])

    def forward_loss():
        Z_cur = np.dot(W, X) + b
        exp_cur = np.exp(Z_cur - np.max(Z_cur, axis=0, keepdims=True))
        A_cur = exp_cur / np.sum(exp_cur, axis=0, keepdims=True)
        return - (1.0 / m) * np.sum(Y * np.log(A_cur + 1e-15))

    rel_err = gradient_check_layer(W, grads["dW1"], forward_loss, eps=1e-5)
    assert rel_err < 1e-6

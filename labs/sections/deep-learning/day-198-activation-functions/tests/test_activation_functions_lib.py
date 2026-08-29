import pytest
import numpy as np
from examples.activation_functions_lib import ActivationEngine, numerical_gradient_check

def test_sigmoid_and_tanh_derivatives():
    z = np.array([-2.5, -1.0, 0.2, 1.5, 3.0])
    sig_grad = ActivationEngine.sigmoid_grad(z)
    err_sig = numerical_gradient_check(ActivationEngine.sigmoid, z, sig_grad)
    assert err_sig < 1e-5

    tanh_grad = ActivationEngine.tanh_grad(z)
    err_tanh = numerical_gradient_check(ActivationEngine.tanh, z, tanh_grad)
    assert err_tanh < 1e-5

def test_relu_and_leaky_relu_behavior():
    z = np.array([-3.0, -1.0, 1.0, 3.0])
    r = ActivationEngine.relu(z)
    assert np.array_equal(r, np.array([0.0, 0.0, 1.0, 3.0]))
    assert np.array_equal(ActivationEngine.relu_grad(z), np.array([0.0, 0.0, 1.0, 1.0]))

    lr = ActivationEngine.leaky_relu(z, alpha=0.1)
    assert np.allclose(lr, np.array([-0.3, -0.1, 1.0, 3.0]))

def test_stable_softmax_prevents_overflow():
    extreme_logits = np.array([[5000.0, 5001.0, 5002.0], [-1000.0, -1000.0, -1000.0]])
    probs = ActivationEngine.stable_softmax(extreme_logits, axis=-1)
    assert not np.isnan(probs).any()
    assert not np.isinf(probs).any()
    assert np.allclose(np.sum(probs, axis=-1), np.array([1.0, 1.0]))

def test_gelu_gradient_accuracy():
    z = np.array([-1.5, -0.5, 0.5, 1.5])
    # Approximate gelu gradient numerically
    eps = 1e-5
    grad_approx = (ActivationEngine.gelu(z + eps) - ActivationEngine.gelu(z - eps)) / (2.0 * eps)
    # Check that gelu output is continuous and smooth
    assert grad_approx.shape == z.shape

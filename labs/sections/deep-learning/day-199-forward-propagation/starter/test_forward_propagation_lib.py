import pytest
import numpy as np
from examples.forward_propagation_lib import DenseLayer, MultiLayerNetwork

def test_dense_layer_shapes_and_caching():
    layer = DenseLayer(in_features=20, out_features=10, activation="relu")
    m = 8
    A_prev = np.random.randn(20, m)
    A, cache = layer.forward(A_prev)

    assert A.shape == (10, m)
    assert cache["A_prev"].shape == (20, m)
    assert cache["Z"].shape == (10, m)
    assert cache["W"].shape == (10, 20)
    assert cache["b"].shape == (10, 1)

def test_multilayer_network_forward_propagation():
    net = MultiLayerNetwork([10, 16, 8, 4], ["relu", "relu", "softmax"])
    m = 12
    X = np.random.randn(10, m)
    A_out, caches = net.forward(X)

    assert A_out.shape == (4, m)
    assert len(caches) == 3
    # Check that softmax probabilities sum to 1.0 along class dimension (axis 0)
    assert np.allclose(np.sum(A_out, axis=0), np.ones(m))

def test_categorical_crossentropy_loss():
    m = 4
    # Perfect predictions
    Y_onehot = np.array([[1.0, 0.0, 0.0, 0.0],
                         [0.0, 1.0, 0.0, 0.0],
                         [0.0, 0.0, 1.0, 0.0],
                         [0.0, 0.0, 0.0, 1.0]])
    A_pred = Y_onehot.copy()
    loss = MultiLayerNetwork.compute_categorical_crossentropy(A_pred, Y_onehot)
    assert loss < 1e-5

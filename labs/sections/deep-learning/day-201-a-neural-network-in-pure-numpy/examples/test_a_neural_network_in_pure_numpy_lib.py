import pytest
import numpy as np
from examples.a_neural_network_in_pure_numpy_lib import NeuralNetwork, generate_two_moons

def test_neural_network_he_initialization():
    net = NeuralNetwork([2, 20, 10, 2], ["relu", "relu", "softmax"])
    assert net.params["W1"].shape == (20, 2)
    assert net.params["b1"].shape == (20, 1)
    assert net.params["W2"].shape == (10, 20)
    assert net.params["W3"].shape == (2, 10)
    # Check that weights are not all zeros
    assert np.count_nonzero(net.params["W1"]) > 0

def test_neural_network_trains_and_reduces_loss():
    X, Y_onehot, _ = generate_two_moons(n_samples=200)
    net = NeuralNetwork([2, 16, 8, 2], ["relu", "relu", "softmax"], learning_rate=0.1)
    losses = net.fit(X, Y_onehot, epochs=50, batch_size=32)

    assert len(losses) == 50
    # Check that loss decreased significantly
    assert losses[-1] < losses[0]

def test_neural_network_achieves_high_accuracy_on_moons():
    X, Y_onehot, y_true = generate_two_moons(n_samples=300)
    net = NeuralNetwork([2, 32, 16, 2], ["relu", "relu", "softmax"], learning_rate=0.1, momentum=0.9)
    net.fit(X, Y_onehot, epochs=80, batch_size=32)

    preds = net.predict(X)
    acc = np.mean(preds == y_true)
    assert acc > 0.90

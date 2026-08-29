import pytest
import numpy as np
from examples.training_mnist_from_scratch_lib import MNISTClassifier, generate_synthetic_mnist

def test_mnist_classifier_parameter_shapes():
    clf = MNISTClassifier(hidden_dim=128)
    assert clf.W1.shape == (128, 784)
    assert clf.b1.shape == (128, 1)
    assert clf.W2.shape == (10, 128)
    assert clf.b2.shape == (10, 1)

def test_mnist_forward_and_loss_evaluation():
    X_tr, Y_tr, y_tr, _, _ = generate_synthetic_mnist(n_train=32, n_test=10)
    clf = MNISTClassifier(hidden_dim=64)
    Z1, A1, Z2, A2 = clf.forward(X_tr)

    assert A2.shape == (10, 32)
    assert np.allclose(np.sum(A2, axis=0), np.ones(32))

    loss, acc = clf.evaluate(X_tr, y_tr)
    assert loss > 0.0
    assert 0.0 <= acc <= 1.0

def test_mnist_training_reduces_loss():
    X_tr, Y_tr, y_tr, _, _ = generate_synthetic_mnist(n_train=128, n_test=32)
    clf = MNISTClassifier(hidden_dim=32, lr=0.1, momentum=0.9)
    loss1 = clf.train_epoch(X_tr, Y_tr, batch_size=32)
    for _ in range(10):
        loss_final = clf.train_epoch(X_tr, Y_tr, batch_size=32)

    assert loss_final < loss1

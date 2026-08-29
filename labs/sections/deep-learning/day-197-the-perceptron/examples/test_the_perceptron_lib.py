import pytest
import numpy as np
from examples.the_perceptron_lib import Perceptron, solve_xor_with_two_layers

def test_perceptron_learns_and_and_or_gates():
    X = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    y_and = np.array([0, 0, 0, 1])
    y_or = np.array([0, 1, 1, 1])

    p_and = Perceptron(learning_rate=0.1, max_epochs=50)
    p_and.fit(X, y_and)
    assert np.array_equal(p_and.predict(X), y_and)

    p_or = Perceptron(learning_rate=0.1, max_epochs=50)
    p_or.fit(X, y_or)
    assert np.array_equal(p_or.predict(X), y_or)

def test_two_layer_mlp_solves_xor():
    truth_table = [
        (0, 0, 0),
        (1, 0, 1),
        (0, 1, 1),
        (1, 1, 0)
    ]
    for x1, x2, expected in truth_table:
        assert solve_xor_with_two_layers(x1, x2) == expected

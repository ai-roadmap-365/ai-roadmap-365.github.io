import numpy as np

class Perceptron:
    def __init__(self, learning_rate: float = 0.1, max_epochs: int = 100):
        self.lr = learning_rate
        self.max_epochs = max_epochs
        self.weights = None
        self.bias = 0.0

    def predict(self, X: np.ndarray) -> np.ndarray:
        # TODO: Compute z = X.w + b and apply step activation
        pass

    def fit(self, X: np.ndarray, y: np.ndarray) -> "Perceptron":
        # TODO: Implement Rosenblatt Perceptron Learning Rule
        pass

def solve_xor_with_two_layers(x1: int, x2: int) -> int:
    # TODO: Implement 2-layer manual MLP solving XOR
    pass

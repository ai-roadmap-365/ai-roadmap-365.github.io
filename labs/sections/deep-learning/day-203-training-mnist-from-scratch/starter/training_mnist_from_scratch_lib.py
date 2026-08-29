import numpy as np
from typing import Tuple, Dict

class MNISTClassifier:
    def __init__(self, hidden_dim: int = 128, lr: float = 0.1, momentum: float = 0.9):
        self.hidden_dim = hidden_dim
        self.lr = lr
        self.beta = momentum
        self.W1 = None
        self.b1 = None
        self.W2 = None
        self.b2 = None

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        # TODO: Implement 2-layer forward pass with ReLU and stable Softmax
        pass

    def train_epoch(self, X: np.ndarray, Y: np.ndarray, batch_size: int = 64) -> float:
        # TODO: Implement mini-batch training loop with Momentum
        pass

    def evaluate(self, X: np.ndarray, y_labels: np.ndarray) -> Tuple[float, float]:
        # TODO: Compute loss and accuracy
        pass

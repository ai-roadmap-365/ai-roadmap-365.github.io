import numpy as np
from typing import List, Tuple, Dict, Any

class DenseLayer:
    def __init__(self, in_features: int, out_features: int, activation: str = "relu"):
        self.in_features = in_features
        self.out_features = out_features
        self.activation = activation
        limit = np.sqrt(2.0 / in_features) if activation == "relu" else np.sqrt(1.0 / in_features)
        self.W = np.random.randn(out_features, in_features) * limit
        self.b = np.zeros((out_features, 1))

    def forward(self, A_prev: np.ndarray) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        Z = np.dot(self.W, A_prev) + self.b

        if self.activation == "relu":
            A = np.maximum(0.0, Z)
        elif self.activation == "sigmoid":
            A = np.where(Z >= 0, 1.0 / (1.0 + np.exp(-Z)), np.exp(Z) / (1.0 + np.exp(Z)))
        elif self.activation == "softmax":
            Z_shift = Z - np.max(Z, axis=0, keepdims=True)
            exp_Z = np.exp(Z_shift)
            A = exp_Z / np.sum(exp_Z, axis=0, keepdims=True)
        else:
            A = Z

        cache = {"A_prev": A_prev, "Z": Z, "W": self.W, "b": self.b}
        return A, cache

class MultiLayerNetwork:
    def __init__(self, layer_dims: List[int], activations: List[str]):
        self.layer_dims = layer_dims
        self.activations = activations
        self.layers = []
        for i in range(len(layer_dims) - 1):
            self.layers.append(DenseLayer(layer_dims[i], layer_dims[i+1], activations[i]))

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, List[Dict[str, np.ndarray]]]:
        A = X
        caches = []
        for layer in self.layers:
            A, cache = layer.forward(A)
            caches.append(cache)
        return A, caches

    @staticmethod
    def compute_categorical_crossentropy(A_last: np.ndarray, Y_onehot: np.ndarray) -> float:
        m = Y_onehot.shape[1]
        eps = 1e-15
        loss = - (1.0 / m) * np.sum(Y_onehot * np.log(A_last + eps))
        return float(loss)

def run_forward_demo():
    np.random.seed(42)
    # Architecture: 784 -> 128 -> 64 -> 10
    net = MultiLayerNetwork([784, 128, 64, 10], ["relu", "relu", "softmax"])
    m = 32
    X = np.random.randn(784, m)
    Y = np.zeros((10, m))
    for i in range(m):
        Y[np.random.randint(0, 10), i] = 1.0

    A_out, caches = net.forward(X)
    loss = net.compute_categorical_crossentropy(A_out, Y)

    print(f"Forward Demo: Output Shape = {A_out.shape}, Initial CCE Loss = {loss:.4f}")
    return A_out, loss

if __name__ == "__main__":
    run_forward_demo()

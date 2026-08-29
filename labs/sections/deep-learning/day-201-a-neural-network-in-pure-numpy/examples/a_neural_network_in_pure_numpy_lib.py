import numpy as np
from typing import List, Tuple, Dict, Any

class NeuralNetwork:
    def __init__(self, layer_dims: List[int], activations: List[str], learning_rate: float = 0.05, momentum: float = 0.9):
        self.layer_dims = layer_dims
        self.activations = activations
        self.lr = learning_rate
        self.beta = momentum
        self.L = len(layer_dims) - 1

        self.params = {}
        self.velocities = {}
        self._initialize_parameters()

    def _initialize_parameters(self):
        np.random.seed(42)
        for l in range(1, self.L + 1):
            n_in = self.layer_dims[l-1]
            n_out = self.layer_dims[l]
            std = np.sqrt(2.0 / n_in) if self.activations[l-1] == "relu" else np.sqrt(1.0 / n_in)
            self.params[f"W{l}"] = np.random.randn(n_out, n_in) * std
            self.params[f"b{l}"] = np.zeros((n_out, 1))

            self.velocities[f"V_dW{l}"] = np.zeros_like(self.params[f"W{l}"])
            self.velocities[f"V_db{l}"] = np.zeros_like(self.params[f"b{l}"])

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, List[Dict[str, np.ndarray]]]:
        A = X
        caches = []
        for l in range(1, self.L + 1):
            W = self.params[f"W{l}"]
            b = self.params[f"b{l}"]
            act = self.activations[l-1]

            Z = np.dot(W, A) + b
            if act == "relu":
                A_next = np.maximum(0.0, Z)
            elif act == "softmax":
                Z_shift = Z - np.max(Z, axis=0, keepdims=True)
                exp_Z = np.exp(Z_shift)
                A_next = exp_Z / np.sum(exp_Z, axis=0, keepdims=True)
            elif act == "sigmoid":
                A_next = np.where(Z >= 0, 1.0 / (1.0 + np.exp(-Z)), np.exp(Z) / (1.0 + np.exp(Z)))
            else:
                A_next = Z

            caches.append({"A_prev": A, "Z": Z, "W": W, "b": b})
            A = A_next

        return A, caches

    def backward(self, A_last: np.ndarray, Y: np.ndarray, caches: List[Dict[str, np.ndarray]]) -> Dict[str, np.ndarray]:
        grads = {}
        m = A_last.shape[1]

        dZ = A_last - Y
        for l in reversed(range(1, self.L + 1)):
            cache = caches[l-1]
            A_prev = cache["A_prev"]
            W = cache["W"]
            Z = cache["Z"]

            if l < self.L:
                act = self.activations[l-1]
                if act == "relu":
                    dZ = dA * np.where(Z > 0.0, 1.0, 0.0)
                elif act == "tanh":
                    dZ = dA * (1.0 - np.tanh(Z) ** 2)

            grads[f"dW{l}"] = (1.0 / m) * np.dot(dZ, A_prev.T)
            grads[f"db{l}"] = (1.0 / m) * np.sum(dZ, axis=1, keepdims=True)
            dA = np.dot(W.T, dZ)

        return grads

    def update_parameters(self, grads: Dict[str, np.ndarray]):
        for l in range(1, self.L + 1):
            self.velocities[f"V_dW{l}"] = self.beta * self.velocities[f"V_dW{l}"] + (1.0 - self.beta) * grads[f"dW{l}"]
            self.velocities[f"V_db{l}"] = self.beta * self.velocities[f"V_db{l}"] + (1.0 - self.beta) * grads[f"db{l}"]

            self.params[f"W{l}"] -= self.lr * self.velocities[f"V_dW{l}"]
            self.params[f"b{l}"] -= self.lr * self.velocities[f"V_db{l}"]

    def fit(self, X: np.ndarray, Y: np.ndarray, epochs: int = 100, batch_size: int = 32) -> List[float]:
        m = X.shape[1]
        loss_history = []

        for epoch in range(epochs):
            permutation = np.random.permutation(m)
            X_shuffled = X[:, permutation]
            Y_shuffled = Y[:, permutation]

            num_batches = int(np.ceil(m / batch_size))
            epoch_loss = 0.0

            for b in range(num_batches):
                start = b * batch_size
                end = min(start + batch_size, m)
                X_batch = X_shuffled[:, start:end]
                Y_batch = Y_shuffled[:, start:end]

                A_out, caches = self.forward(X_batch)
                batch_loss = - (1.0 / (end - start)) * np.sum(Y_batch * np.log(A_out + 1e-15))
                epoch_loss += batch_loss * (end - start)

                grads = self.backward(A_out, Y_batch, caches)
                self.update_parameters(grads)

            loss_history.append(float(epoch_loss / m))

        return loss_history

    def predict(self, X: np.ndarray) -> np.ndarray:
        A_out, _ = self.forward(X)
        return np.argmax(A_out, axis=0)

def generate_two_moons(n_samples: int = 400) -> Tuple[np.ndarray, np.ndarray]:
    np.random.seed(42)
    n = n_samples // 2
    theta = np.linspace(0, np.pi, n)
    moon1_x = np.cos(theta) + np.random.randn(n) * 0.08
    moon1_y = np.sin(theta) + np.random.randn(n) * 0.08

    moon2_x = 1 - np.cos(theta) + np.random.randn(n) * 0.08
    moon2_y = 1 - np.sin(theta) - 0.5 + np.random.randn(n) * 0.08

    X = np.vstack([np.hstack([moon1_x, moon2_x]), np.hstack([moon1_y, moon2_y])])
    y = np.hstack([np.zeros(n, dtype=int), np.ones(n, dtype=int)])

    Y_onehot = np.zeros((2, n_samples))
    for i in range(n_samples):
        Y_onehot[y[i], i] = 1.0

    return X, Y_onehot, y

def run_pure_numpy_demo():
    X, Y_onehot, y_true = generate_two_moons(n_samples=300)
    net = NeuralNetwork([2, 16, 8, 2], ["relu", "relu", "softmax"], learning_rate=0.1, momentum=0.9)
    losses = net.fit(X, Y_onehot, epochs=60, batch_size=32)

    preds = net.predict(X)
    acc = float(np.mean(preds == y_true))

    print(f"Pure NumPy Demo: Final Loss = {losses[-1]:.4f}, Accuracy = {acc * 100:.1f}%")
    return net, acc

if __name__ == "__main__":
    run_pure_numpy_demo()

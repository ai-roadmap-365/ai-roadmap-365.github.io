import numpy as np

class Perceptron:
    def __init__(self, learning_rate: float = 0.1, max_epochs: int = 100):
        self.lr = learning_rate
        self.max_epochs = max_epochs
        self.weights = None
        self.bias = 0.0
        self.errors_per_epoch = []

    def predict(self, X: np.ndarray) -> np.ndarray:
        z = np.dot(X, self.weights) + self.bias
        return np.where(z >= 0.0, 1, 0)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "Perceptron":
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features, dtype=float)
        self.bias = 0.0
        self.errors_per_epoch = []

        for epoch in range(self.max_epochs):
            total_errors = 0
            for i in range(n_samples):
                xi = X[i]
                target = y[i]
                y_hat = 1 if (np.dot(xi, self.weights) + self.bias) >= 0.0 else 0
                error = target - y_hat

                if error != 0:
                    self.weights += self.lr * error * xi
                    self.bias += self.lr * error
                    total_errors += 1

            self.errors_per_epoch.append(total_errors)
            if total_errors == 0:
                break

        return self

def solve_xor_with_two_layers(x1: int, x2: int) -> int:
    # Hidden Layer: NAND and OR
    h_nand = 1 if (-2.0 * x1 + -2.0 * x2 + 3.0) >= 0.0 else 0
    h_or = 1 if (2.0 * x1 + 2.0 * x2 - 1.0) >= 0.0 else 0
    # Output Layer: AND of hidden gates
    y_xor = 1 if (2.0 * h_nand + 2.0 * h_or - 3.0) >= 0.0 else 0
    return y_xor

def run_perceptron_demo():
    X = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    y_and = np.array([0, 0, 0, 1])

    p = Perceptron(learning_rate=0.1, max_epochs=20)
    p.fit(X, y_and)
    preds = p.predict(X)

    print(f"Perceptron Demo: AND Gate Predictions = {preds.tolist()}, Epochs = {len(p.errors_per_epoch)}")
    return p, preds

if __name__ == "__main__":
    run_perceptron_demo()

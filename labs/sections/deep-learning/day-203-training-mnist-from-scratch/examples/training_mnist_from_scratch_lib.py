import numpy as np
from typing import Tuple, Dict

class MNISTClassifier:
    def __init__(self, hidden_dim: int = 128, lr: float = 0.1, momentum: float = 0.9):
        self.hidden_dim = hidden_dim
        self.lr = lr
        self.beta = momentum

        np.random.seed(42)
        self.W1 = np.random.randn(hidden_dim, 784) * np.sqrt(2.0 / 784.0)
        self.b1 = np.zeros((hidden_dim, 1))
        self.W2 = np.random.randn(10, hidden_dim) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros((10, 1))

        self.V_dW1 = np.zeros_like(self.W1)
        self.V_db1 = np.zeros_like(self.b1)
        self.V_dW2 = np.zeros_like(self.W2)
        self.V_db2 = np.zeros_like(self.b2)

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        Z1 = np.dot(self.W1, X) + self.b1
        A1 = np.maximum(0.0, Z1)

        Z2 = np.dot(self.W2, A1) + self.b2
        exp_Z2 = np.exp(Z2 - np.max(Z2, axis=0, keepdims=True))
        A2 = exp_Z2 / np.sum(exp_Z2, axis=0, keepdims=True)

        return Z1, A1, Z2, A2

    def train_epoch(self, X: np.ndarray, Y: np.ndarray, batch_size: int = 64) -> float:
        m = X.shape[1]
        p = np.random.permutation(m)
        X_shuf = X[:, p]
        Y_shuf = Y[:, p]

        num_batches = int(np.ceil(m / batch_size))
        total_loss = 0.0

        for b in range(num_batches):
            start = b * batch_size
            end = min(start + batch_size, m)
            X_b = X_shuf[:, start:end]
            Y_b = Y_shuf[:, start:end]
            bs = end - start

            Z1, A1, Z2, A2 = self.forward(X_b)
            loss = - (1.0 / bs) * np.sum(Y_b * np.log(A2 + 1e-15))
            total_loss += loss * bs

            dZ2 = A2 - Y_b
            dW2 = (1.0 / bs) * np.dot(dZ2, A1.T)
            db2 = (1.0 / bs) * np.sum(dZ2, axis=1, keepdims=True)

            dA1 = np.dot(self.W2.T, dZ2)
            dZ1 = dA1 * np.where(Z1 > 0.0, 1.0, 0.0)
            dW1 = (1.0 / bs) * np.dot(dZ1, X_b.T)
            db1 = (1.0 / bs) * np.sum(dZ1, axis=1, keepdims=True)

            self.V_dW2 = self.beta * self.V_dW2 + (1.0 - self.beta) * dW2
            self.V_db2 = self.beta * self.V_db2 + (1.0 - self.beta) * db2
            self.V_dW1 = self.beta * self.V_dW1 + (1.0 - self.beta) * dW1
            self.V_db1 = self.beta * self.V_db1 + (1.0 - self.beta) * db1

            self.W2 -= self.lr * self.V_dW2
            self.b2 -= self.lr * self.V_db2
            self.W1 -= self.lr * self.V_dW1
            self.b1 -= self.lr * self.V_db1

        return float(total_loss / m)

    def evaluate(self, X: np.ndarray, y_labels: np.ndarray) -> Tuple[float, float]:
        _, _, _, A2 = self.forward(X)
        preds = np.argmax(A2, axis=0)
        acc = float(np.mean(preds == y_labels))

        m = X.shape[1]
        Y = np.zeros((10, m))
        for i in range(m):
            Y[y_labels[i], i] = 1.0
        loss = float(- (1.0 / m) * np.sum(Y * np.log(A2 + 1e-15)))
        return loss, acc

def generate_synthetic_mnist(n_train: int = 500, n_test: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    np.random.seed(42)
    # Generate structured synthetic digits for fast unit test verification
    X_train = np.random.rand(784, n_train).astype(np.float32)
    y_train = np.random.randint(0, 10, size=n_train)

    X_test = np.random.rand(784, n_test).astype(np.float32)
    y_test = np.random.randint(0, 10, size=n_test)

    Y_train_onehot = np.zeros((10, n_train))
    for i in range(n_train):
        Y_train_onehot[y_train[i], i] = 1.0

    return X_train, Y_train_onehot, y_train, X_test, y_test

def run_mnist_demo():
    X_tr, Y_tr, y_tr, X_te, y_te = generate_synthetic_mnist(n_train=400, n_test=100)
    model = MNISTClassifier(hidden_dim=64, lr=0.05, momentum=0.9)
    for ep in range(5):
        loss = model.train_epoch(X_tr, Y_tr, batch_size=32)

    val_loss, val_acc = model.evaluate(X_te, y_te)
    print(f"MNIST Demo: Final Train Loss = {loss:.4f}, Val Loss = {val_loss:.4f}, Val Acc = {val_acc*100:.1f}%")
    return model, val_acc

if __name__ == "__main__":
    run_mnist_demo()

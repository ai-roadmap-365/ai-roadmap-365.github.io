import numpy as np
from typing import List, Dict, Tuple, Any

class BackpropEngine:
    @staticmethod
    def relu_backward(dA: np.ndarray, Z: np.ndarray) -> np.ndarray:
        dZ = np.array(dA, copy=True)
        dZ[Z <= 0.0] = 0.0
        return dZ

    @staticmethod
    def tanh_backward(dA: np.ndarray, Z: np.ndarray) -> np.ndarray:
        return dA * (1.0 - np.tanh(Z) ** 2)

    @staticmethod
    def linear_backward(dZ: np.ndarray, cache: Dict[str, np.ndarray]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        A_prev = cache["A_prev"]
        W = cache["W"]
        b = cache["b"]
        m = A_prev.shape[1]

        dW = (1.0 / m) * np.dot(dZ, A_prev.T)
        db = (1.0 / m) * np.sum(dZ, axis=1, keepdims=True)
        dA_prev = np.dot(W.T, dZ)

        return dA_prev, dW, db

    @staticmethod
    def full_backward_pass(A_last: np.ndarray, Y: np.ndarray, caches: List[Dict[str, np.ndarray]], activations: List[str]) -> Dict[str, np.ndarray]:
        grads = {}
        L = len(caches)

        dZ_last = A_last - Y
        dA_prev, dW_last, db_last = BackpropEngine.linear_backward(dZ_last, caches[L-1])
        grads[f"dW{L}"] = dW_last
        grads[f"db{L}"] = db_last
        dA = dA_prev

        for l in reversed(range(L - 1)):
            cache = caches[l]
            act = activations[l]
            Z = cache["Z"]

            if act == "relu":
                dZ = BackpropEngine.relu_backward(dA, Z)
            elif act == "tanh":
                dZ = BackpropEngine.tanh_backward(dA, Z)
            else:
                dZ = dA

            dA_prev, dW, db = BackpropEngine.linear_backward(dZ, cache)
            grads[f"dW{l+1}"] = dW
            grads[f"db{l+1}"] = db
            dA = dA_prev

        return grads

def gradient_check_layer(W: np.ndarray, dW_analytical: np.ndarray, forward_fn, eps: float = 1e-5) -> float:
    # Compute numerical gradient for a weight matrix
    dW_num = np.zeros_like(W)
    for i in range(W.shape[0]):
        for j in range(W.shape[1]):
            orig = W[i, j]
            W[i, j] = orig + eps
            loss_plus = forward_fn()
            W[i, j] = orig - eps
            loss_minus = forward_fn()
            W[i, j] = orig
            dW_num[i, j] = (loss_plus - loss_minus) / (2.0 * eps)

    num = np.linalg.norm(dW_analytical - dW_num)
    den = np.linalg.norm(dW_analytical) + np.linalg.norm(dW_num) + 1e-8
    return float(num / den)

def run_backprop_demo():
    np.random.seed(42)
    m = 16
    X = np.random.randn(8, m)
    Y = np.zeros((3, m))
    for i in range(m):
        Y[np.random.randint(0, 3), i] = 1.0

    # Layer 1: 8 -> 16
    W1 = np.random.randn(16, 8) * 0.1
    b1 = np.zeros((16, 1))
    Z1 = np.dot(W1, X) + b1
    A1 = np.maximum(0.0, Z1)

    # Layer 2: 16 -> 3
    W2 = np.random.randn(3, 16) * 0.1
    b2 = np.zeros((3, 1))
    Z2 = np.dot(W2, A1) + b2
    exp_Z2 = np.exp(Z2 - np.max(Z2, axis=0, keepdims=True))
    A2 = exp_Z2 / np.sum(exp_Z2, axis=0, keepdims=True)

    caches = [
        {"A_prev": X, "Z": Z1, "W": W1, "b": b1},
        {"A_prev": A1, "Z": Z2, "W": W2, "b": b2}
    ]
    grads = BackpropEngine.full_backward_pass(A2, Y, caches, ["relu", "softmax"])

    print(f"Backprop Demo: dW2 Shape = {grads['dW2'].shape}, dW1 Shape = {grads['dW1'].shape}")
    return grads

if __name__ == "__main__":
    run_backprop_demo()

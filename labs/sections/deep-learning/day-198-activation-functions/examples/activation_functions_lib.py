import numpy as np

class ActivationEngine:
    @staticmethod
    def sigmoid(z: np.ndarray) -> np.ndarray:
        return np.where(z >= 0, 1.0 / (1.0 + np.exp(-z)), np.exp(z) / (1.0 + np.exp(z)))

    @staticmethod
    def sigmoid_grad(z: np.ndarray) -> np.ndarray:
        s = ActivationEngine.sigmoid(z)
        return s * (1.0 - s)

    @staticmethod
    def tanh(z: np.ndarray) -> np.ndarray:
        return np.tanh(z)

    @staticmethod
    def tanh_grad(z: np.ndarray) -> np.ndarray:
        t = np.tanh(z)
        return 1.0 - t ** 2

    @staticmethod
    def relu(z: np.ndarray) -> np.ndarray:
        return np.maximum(0.0, z)

    @staticmethod
    def relu_grad(z: np.ndarray) -> np.ndarray:
        return np.where(z > 0.0, 1.0, 0.0)

    @staticmethod
    def leaky_relu(z: np.ndarray, alpha: float = 0.01) -> np.ndarray:
        return np.where(z > 0.0, z, alpha * z)

    @staticmethod
    def leaky_relu_grad(z: np.ndarray, alpha: float = 0.01) -> np.ndarray:
        return np.where(z > 0.0, 1.0, alpha)

    @staticmethod
    def gelu(z: np.ndarray) -> np.ndarray:
        return 0.5 * z * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (z + 0.044715 * (z ** 3))))

    @staticmethod
    def stable_softmax(z: np.ndarray, axis: int = -1) -> np.ndarray:
        z_shifted = z - np.max(z, axis=axis, keepdims=True)
        exp_z = np.exp(z_shifted)
        return exp_z / np.sum(exp_z, axis=axis, keepdims=True)

def numerical_gradient_check(func, z: np.ndarray, analytical_grad: np.ndarray, eps: float = 1e-5) -> float:
    grad_approx = (func(z + eps) - func(z - eps)) / (2.0 * eps)
    numerator = np.linalg.norm(analytical_grad - grad_approx)
    denominator = np.linalg.norm(analytical_grad) + np.linalg.norm(grad_approx) + 1e-8
    return float(numerator / denominator)

def run_activation_demo():
    z = np.array([-2.0, -0.5, 0.0, 0.5, 2.0])
    s = ActivationEngine.sigmoid(z)
    sg = ActivationEngine.sigmoid_grad(z)
    err = numerical_gradient_check(ActivationEngine.sigmoid, z, sg)

    extreme_logits = np.array([[1000.0, 2000.0, 3000.0]])
    probs = ActivationEngine.stable_softmax(extreme_logits)

    print(f"Activation Demo: Sigmoid Relative Error = {err:.4e}, Stable Softmax Sum = {np.sum(probs):.4f}")
    return s, probs

if __name__ == "__main__":
    run_activation_demo()

import numpy as np
from typing import Tuple, Dict, Any

class PyTorchTensorToolkit:
    @staticmethod
    def tensor_strides_demo(arr: np.ndarray) -> Dict[str, Any]:
        shape = arr.shape
        strides = arr.strides
        is_c_contiguous = arr.flags["C_CONTIGUOUS"]
        # Transpose
        arr_t = arr.T
        is_t_contiguous = arr_t.flags["C_CONTIGUOUS"]
        # Make contiguous and flatten
        flattened = np.ascontiguousarray(arr_t).reshape(-1)

        return {
            "orig_shape": shape,
            "orig_strides": strides,
            "orig_contiguous": is_c_contiguous,
            "transposed_contiguous": is_t_contiguous,
            "flattened_shape": flattened.shape
        }

    @staticmethod
    def linear_autograd_simulation(X: np.ndarray, W: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Forward pass: Z = W X + b, Loss = sum(Z^2)
        Z = np.dot(W, X) + b
        loss = float(np.sum(Z ** 2))

        # Backward pass: dL/dZ = 2 * Z
        dZ = 2.0 * Z
        dW = np.dot(dZ, X.T)
        db = np.sum(dZ, axis=1, keepdims=True)

        return Z, dW, db

def run_pytorch_tensors_demo():
    X = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    W = np.array([[0.5, -0.5], [1.0, 2.0]], dtype=np.float32)
    b = np.array([[0.1], [-0.1]], dtype=np.float32)

    Z, dW, db = PyTorchTensorToolkit.linear_autograd_simulation(X, W, b)
    print(f"PyTorch Tensors Demo: Output Z shape = {Z.shape}, dW shape = {dW.shape}")
    return Z, dW, db

if __name__ == "__main__":
    run_pytorch_tensors_demo()

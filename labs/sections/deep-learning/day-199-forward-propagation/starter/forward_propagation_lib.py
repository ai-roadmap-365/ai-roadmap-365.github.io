import numpy as np
from typing import List, Tuple, Dict, Any

class DenseLayer:
    def __init__(self, in_features: int, out_features: int, activation: str = "relu"):
        self.in_features = in_features
        self.out_features = out_features
        self.activation = activation
        self.W = None
        self.b = None

    def forward(self, A_prev: np.ndarray) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        # TODO: Compute Z = W.A_prev + b, apply activation, and return (A, cache)
        pass

class MultiLayerNetwork:
    def __init__(self, layer_dims: List[int], activations: List[str]):
        # TODO: Initialize layers list
        pass

    def forward(self, X: np.ndarray) -> Tuple[np.ndarray, List[Dict[str, np.ndarray]]]:
        # TODO: Execute layer-by-layer forward propagation
        pass

    @staticmethod
    def compute_categorical_crossentropy(A_last: np.ndarray, Y_onehot: np.ndarray) -> float:
        # TODO: Compute CCE loss
        pass

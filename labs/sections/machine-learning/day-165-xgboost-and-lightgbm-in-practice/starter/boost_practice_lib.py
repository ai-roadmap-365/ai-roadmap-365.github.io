"""
XGBoost and LightGBM algorithmic foundations starter library.
"""
import numpy as np


def compute_xgboost_split_gain(
    g_l: float, h_l: float, g_r: float, h_r: float, reg_lambda: float = 1.0, gamma: float = 0.0
) -> float:
    """Compute exact second-order XGBoost split gain."""
    raise NotImplementedError("Implement compute_xgboost_split_gain")


def histogram_bin_feature(x: np.ndarray, n_bins: int = 256) -> tuple[np.ndarray, np.ndarray]:
    """Discretize continuous feature into integer bins [0, n_bins-1]."""
    raise NotImplementedError("Implement histogram_bin_feature")


class HistogramGBSimplified:
    def __init__(self, n_estimators: int = 20, learning_rate: float = 0.1, max_leaf_nodes: int = 31):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_leaf_nodes = max_leaf_nodes
        self.model = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit histogram-based gradient booster with native missing value support."""
        raise NotImplementedError("Implement fit")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        raise NotImplementedError("Implement predict")

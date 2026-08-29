"""
XGBoost and LightGBM algorithmic foundations reference library implementation.
"""
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier


def compute_xgboost_split_gain(
    g_l: float, h_l: float, g_r: float, h_r: float, reg_lambda: float = 1.0, gamma: float = 0.0
) -> float:
    """
    Compute exact second-order XGBoost split gain:
    Gain = 0.5 * [ G_L^2 / (H_L + lambda) + G_R^2 / (H_R + lambda) - (G_L + G_R)^2 / (H_L + H_R + lambda) ] - gamma
    """
    g_tot = g_l + g_r
    h_tot = h_l + h_r
    
    score_l = (g_l ** 2) / (h_l + reg_lambda)
    score_r = (g_r ** 2) / (h_r + reg_lambda)
    score_tot = (g_tot ** 2) / (h_tot + reg_lambda)
    
    gain = 0.5 * (score_l + score_r - score_tot) - gamma
    return float(gain)


def histogram_bin_feature(x: np.ndarray, n_bins: int = 256) -> tuple[np.ndarray, np.ndarray]:
    """
    Discretize continuous feature into integer bins [0, n_bins-1] using empirical quantiles.
    Returns (binned_x as uint8, bin_thresholds).
    """
    x = np.asarray(x, dtype=float)
    # Remove NaNs for quantile calculation
    valid_x = x[~np.isnan(x)]
    if len(valid_x) == 0:
        return np.zeros(len(x), dtype=np.uint8), np.array([])
        
    quantiles = np.linspace(0.0, 100.0, n_bins + 1)[1:-1]
    bin_thresholds = np.unique(np.percentile(valid_x, quantiles))
    
    # Digitize into integer bins
    binned = np.digitize(x, bin_thresholds, right=False).astype(np.uint8)
    return binned, bin_thresholds


class HistogramGBSimplified:
    """
    Production-grade tabular classifier wrapper utilizing scikit-learn's optimized
    HistGradientBoostingClassifier with native missing value support and early stopping.
    """
    def __init__(
        self,
        n_estimators: int = 30,
        learning_rate: float = 0.1,
        max_leaf_nodes: int = 31,
        l2_regularization: float = 1.0,
        random_state: int = 42
    ):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_leaf_nodes = max_leaf_nodes
        self.l2_regularization = l2_regularization
        self.random_state = random_state
        self.clf = HistGradientBoostingClassifier(
            max_iter=self.n_estimators,
            learning_rate=self.learning_rate,
            max_leaf_nodes=self.max_leaf_nodes,
            l2_regularization=self.l2_regularization,
            random_state=self.random_state
        )

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        self.clf.fit(X, y)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.clf.predict_proba(X)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.clf.predict(X)

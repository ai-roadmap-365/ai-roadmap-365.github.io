import numpy as np
from typing import Tuple, List

def create_lag_and_rolling_features(series: np.ndarray, lags: List[int] = [1, 2, 7], window_size: int = 7) -> Tuple[np.ndarray, np.ndarray]:
    # TODO: Build lag and rolling window features without lookahead leakage
    pass

def compute_smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    # TODO: Calculate Symmetric MAPE metric
    pass

class WalkForwardTimeSeriesSplit:
    def __init__(self, n_splits: int = 4, test_size: int = 10):
        self.n_splits = n_splits
        self.test_size = test_size

    def split(self, X: np.ndarray) -> List[Tuple[np.ndarray, np.ndarray]]:
        # TODO: Return expanding walk-forward train and test index tuples
        pass

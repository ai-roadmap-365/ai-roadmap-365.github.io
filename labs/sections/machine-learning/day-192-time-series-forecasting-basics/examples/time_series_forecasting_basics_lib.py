import numpy as np
from typing import Tuple, List

def create_lag_and_rolling_features(
    series: np.ndarray, lags: List[int] = [1, 2, 7], window_size: int = 7
) -> Tuple[np.ndarray, np.ndarray]:
    n = len(series)
    max_lag = max(max(lags), window_size)
    features = []
    targets = []

    for t in range(max_lag, n):
        row = []
        for lag in lags:
            row.append(series[t - lag])
        past_window = series[t - window_size : t]
        row.append(float(np.mean(past_window)))
        row.append(float(np.std(past_window)))

        features.append(row)
        targets.append(series[t])

    return np.array(features, dtype=float), np.array(targets, dtype=float)

def compute_smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    denom = np.abs(y_true) + np.abs(y_pred) + 1e-12
    return float(100.0 * np.mean(2.0 * np.abs(y_true - y_pred) / denom))

class WalkForwardTimeSeriesSplit:
    def __init__(self, n_splits: int = 4, test_size: int = 10):
        self.n_splits = n_splits
        self.test_size = test_size

    def split(self, X: np.ndarray) -> List[Tuple[np.ndarray, np.ndarray]]:
        n_samples = len(X)
        splits = []
        for i in range(self.n_splits):
            test_end = n_samples - (self.n_splits - 1 - i) * self.test_size
            test_start = test_end - self.test_size
            train_end = test_start

            train_idx = np.arange(0, train_end)
            test_idx = np.arange(test_start, test_end)
            splits.append((train_idx, test_idx))
        return splits

def run_forecasting_demo():
    np.random.seed(42)
    t = np.arange(100)
    series = 50.0 + 0.5 * t + 10.0 * np.sin(2 * np.pi * t / 7) + np.random.normal(0, 1, 100)
    X, y = create_lag_and_rolling_features(series, lags=[1, 7], window_size=7)
    splitter = WalkForwardTimeSeriesSplit(n_splits=3, test_size=10)
    splits = splitter.split(X)

    print(f"Forecasting Demo: Features Shape {X.shape}, Walk-Forward Splits Count = {len(splits)}")
    return X, y, splits

if __name__ == "__main__":
    run_forecasting_demo()

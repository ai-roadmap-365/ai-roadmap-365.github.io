"""
Scikit-Learn Pipelines reference library implementation.
"""
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder


class CustomLogTransformer(BaseEstimator, TransformerMixin):
    """
    Log1p feature transformer: z = log(max(x, 0) + offset)
    Compatible with scikit-learn clone() and get_params().
    """
    def __init__(self, offset: float = 1.0):
        self.offset = offset

    def fit(self, X, y=None):
        # Stateless transformer validation
        X = np.asarray(X, dtype=float)
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=float)
        clipped = np.maximum(X, 0.0)
        return np.log(clipped + self.offset)


class OutlierClipperTransformer(BaseEstimator, TransformerMixin):
    """
    Fits empirical percentile thresholds on training data:
    lower_bound = percentile(X, lower_p)
    upper_bound = percentile(X, upper_p)
    Clips incoming data to [lower_bound, upper_bound] to guard against extreme anomalies.
    """
    def __init__(self, lower_percentile: float = 1.0, upper_percentile: float = 99.0):
        self.lower_percentile = lower_percentile
        self.upper_percentile = upper_percentile
        self.lower_bounds_ = None
        self.upper_bounds_ = None

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.lower_bounds_ = np.percentile(X, self.lower_percentile, axis=0)
        self.upper_bounds_ = np.percentile(X, self.upper_percentile, axis=0)
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=float)
        if self.lower_bounds_ is None or self.upper_bounds_ is None:
            raise RuntimeError("Transformer has not been fitted yet!")
        return np.clip(X, self.lower_bounds_, self.upper_bounds_)


def build_heterogeneous_tabular_pipeline(num_indices: list[int], cat_indices: list[int], estimator) -> Pipeline:
    """
    Constructs a complete leak-free heterogeneous preprocessing and modeling Pipeline:
    - Numerical Branch: OutlierClipper -> StandardScaler
    - Categorical Branch: OneHotEncoder(handle_unknown='ignore')
    - Final Step: Estimator
    """
    num_pipeline = Pipeline([
        ("clipper", OutlierClipperTransformer(lower_percentile=1.0, upper_percentile=99.0)),
        ("scaler", StandardScaler())
    ])
    
    cat_pipeline = Pipeline([
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, num_indices),
            ("cat", cat_pipeline, cat_indices)
        ],
        remainder="drop"
    )
    
    full_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("estimator", estimator)
    ])
    
    return full_pipeline

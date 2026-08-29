"""
Scikit-Learn Pipelines starter library.
"""
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer


class CustomLogTransformer(BaseEstimator, TransformerMixin):
    """Stateless or offset log transformer: log(x + offset)."""
    def __init__(self, offset: float = 1.0):
        self.offset = offset

    def fit(self, X, y=None):
        raise NotImplementedError("Implement fit")

    def transform(self, X):
        raise NotImplementedError("Implement transform")


class OutlierClipperTransformer(BaseEstimator, TransformerMixin):
    """Clips numerical features to empirical percentile bounds [lower_p, upper_p]."""
    def __init__(self, lower_percentile: float = 1.0, upper_percentile: float = 99.0):
        self.lower_percentile = lower_percentile
        self.upper_percentile = upper_percentile
        self.lower_bounds_ = None
        self.upper_bounds_ = None

    def fit(self, X, y=None):
        raise NotImplementedError("Implement fit")

    def transform(self, X):
        raise NotImplementedError("Implement transform")


def build_heterogeneous_tabular_pipeline(num_indices: list[int], cat_indices: list[int], estimator) -> Pipeline:
    """Build end-to-end ColumnTransformer and Estimator Pipeline."""
    raise NotImplementedError("Implement build_heterogeneous_tabular_pipeline")

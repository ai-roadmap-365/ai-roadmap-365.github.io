"""
Naive Bayes starter library.
"""
import numpy as np
import re


def tokenize(text: str) -> list[str]:
    """Tokenize raw text into lowercase alphanumeric words."""
    raise NotImplementedError("Implement tokenize")


def build_vocabulary(corpus: list[str]) -> dict[str, int]:
    """Build word-to-index mapping from a list of documents."""
    raise NotImplementedError("Implement build_vocabulary")


def text_to_bow(corpus: list[str], vocab: dict[str, int]) -> np.ndarray:
    """Convert text corpus into a Bag-of-Words count matrix."""
    raise NotImplementedError("Implement text_to_bow")


class ScratchMultinomialNB:
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.class_log_prior_ = None
        self.feature_log_prob_ = None
        self.classes_ = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit Multinomial Naive Bayes parameters with Laplace smoothing."""
        raise NotImplementedError("Implement fit")

    def predict_log_proba(self, X: np.ndarray) -> np.ndarray:
        """Compute joint log likelihood for each class."""
        raise NotImplementedError("Implement predict_log_proba")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        raise NotImplementedError("Implement predict")

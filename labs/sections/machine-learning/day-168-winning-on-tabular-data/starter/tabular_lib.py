"""
Winning on Tabular Data starter library.
"""
import numpy as np


def generate_out_of_fold_predictions(models: list, X: np.ndarray, y: np.ndarray, cv: int = 5) -> np.ndarray:
    """Generate out-of-fold probability predictions for Level-1 meta-learning."""
    raise NotImplementedError("Implement generate_out_of_fold_predictions")


def fit_stacking_ensemble(level0_models: list, meta_learner, X: np.ndarray, y: np.ndarray, cv: int = 5) -> tuple[list, object]:
    """Fit a 2-level stacking ensemble using out-of-fold predictions."""
    raise NotImplementedError("Implement fit_stacking_ensemble")


def predict_stacking_ensemble(fitted_level0: list, meta_learner, X_test: np.ndarray) -> np.ndarray:
    """Predict probabilities or labels using fitted base models and meta-learner."""
    raise NotImplementedError("Implement predict_stacking_ensemble")


def compute_permutation_importance(model, X_val: np.ndarray, y_val: np.ndarray, n_repeats: int = 5) -> np.ndarray:
    """Compute mean accuracy drop when each feature column is randomly shuffled."""
    raise NotImplementedError("Implement compute_permutation_importance")

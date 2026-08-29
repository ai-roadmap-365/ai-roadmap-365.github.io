import numpy as np
from sklearn.model_selection import learning_curve, validation_curve
from sklearn.base import clone

def compute_learning_curves(estimator, X, y, train_sizes=None, cv=5, scoring="r2"):
    """
    Compute training and validation scores across increasing training sample sizes.
    """
    if train_sizes is None:
        train_sizes = np.linspace(0.1, 1.0, 5)
        
    sizes, train_scores, val_scores = learning_curve(
        estimator, X, y, train_sizes=train_sizes, cv=cv, scoring=scoring, n_jobs=1, random_state=42
    )
    
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1)
    
    return {
        "train_sizes": sizes.tolist(),
        "train_scores_mean": train_mean.tolist(),
        "train_scores_std": train_std.tolist(),
        "val_scores_mean": val_mean.tolist(),
        "val_scores_std": val_std.tolist(),
    }

def compute_validation_curves(estimator, X, y, param_name, param_range, cv=5, scoring="r2"):
    """
    Compute training and validation scores across a single hyperparameter range.
    """
    train_scores, val_scores = validation_curve(
        estimator, X, y, param_name=param_name, param_range=param_range, cv=cv, scoring=scoring, n_jobs=1
    )
    
    return {
        "param_name": param_name,
        "param_range": list(param_range),
        "train_scores_mean": np.mean(train_scores, axis=1).tolist(),
        "val_scores_mean": np.mean(val_scores, axis=1).tolist(),
    }

def diagnose_model_regime(train_score, val_score, benchmark_score=0.90, generalization_gap_threshold=0.15):
    """
    Diagnose whether a model is suffering from High Bias (Underfitting), High Variance (Overfitting),
    or operating in the Optimal Tradeoff Regime.
    """
    gap = train_score - val_score
    
    if train_score < (benchmark_score - 0.15) and val_score < (benchmark_score - 0.15):
        return {
            "regime": "HIGH_BIAS",
            "diagnosis": "Underfitting: Model has insufficient representational capacity. Both training and validation errors are unacceptably high.",
            "actionable_remedies": [
                "Add polynomial features or interaction terms",
                "Decrease regularization strength (e.g. reduce Ridge alpha or L1 penalty)",
                "Increase model complexity (e.g. deeper decision trees, more neural units)",
                "Note: Adding more training data will NOT resolve high bias"
            ]
        }
    elif gap > generalization_gap_threshold:
        return {
            "regime": "HIGH_VARIANCE",
            "diagnosis": "Overfitting: Model memorized training noise. Large generalization gap between training and validation scores.",
            "actionable_remedies": [
                "Collect more training data (learning curve shows validation error steadily decreasing)",
                "Increase regularization strength (increase L2 weight decay / Ridge alpha)",
                "Apply feature selection to prune uninformative noise dimensions",
                "Apply ensemble bagging / Random Forests with subspace sampling"
            ]
        }
    else:
        return {
            "regime": "OPTIMAL",
            "diagnosis": "Optimal Regime: Balanced bias-variance tradeoff with high validation performance and low generalization gap.",
            "actionable_remedies": ["Model is ready for holdout testing and canary deployment"]
        }

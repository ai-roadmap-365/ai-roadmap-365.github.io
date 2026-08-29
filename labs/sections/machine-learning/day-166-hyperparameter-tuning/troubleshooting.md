# Troubleshooting Guide for Day 166

## Common Issues

### 1. Exponential Computational Explosion in Grid Search
- **Symptom:** Tuning script hangs for hours or days without finishing.
- **Cause:** Adding 5 parameters with 5 values each creates `5^5 = 3,125` configurations; with 5-fold CV, that requires `15,625` model training runs.
- **Fix:** Switch from exhaustive Grid Search to Random Search (`n_iter=50`) or Bayesian Optimization (Optuna / Hyperband).

### 2. Information Leakage and Overfitting to the Validation Set
- **Symptom:** Validation tuning score is 99% but test score drops to 85%.
- **Cause:** Evaluating 10,000 hyperparameter trials on a small single validation set selects a model that overfit random validation noise.
- **Fix:** Use Nested Cross-Validation or a completely isolated holdout test set that is touched only once after tuning completes.

# Troubleshooting Guide for Day 164

## Common Issues

### 1. Vanishing or Exploding Probabilities in Log-Loss Newton-Raphson Denominator
- **Symptom:** `ZeroDivisionError` or `NaN` values during leaf value calculation `sum(r) / sum(p * (1-p))`.
- **Cause:** When predicted probabilities approach `0.0` or `1.0`, the variance `p * (1 - p)` vanishes to zero.
- **Fix:** Add a numerical stabilizer `1e-15` to the denominator: `den = np.sum(p * (1 - p)) + 1e-15`.

### 2. Overfitting Due to High Learning Rate or Excessive Estimators
- **Symptom:** Training error drops to 0.0 immediately while test loss explodes.
- **Cause:** Gradient boosting minimizes empirical loss aggressively; large learning rate (`eta > 0.3`) without shrinkage memorizes noise.
- **Fix:** Decrease learning rate to `eta = 0.05` to `0.1` and use early stopping with validation loss monitoring.

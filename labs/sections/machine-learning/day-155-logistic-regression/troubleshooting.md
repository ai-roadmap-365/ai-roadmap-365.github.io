# Troubleshooting Guide for Day 155

## Common Issues

### 1. Overflow in Sigmoid Computation (`exp` overflow)
- **Symptom:** `RuntimeWarning: overflow encountered in exp` when calculating `1.0 / (1.0 + np.exp(-z))`.
- **Cause:** Large negative values of `z` cause `np.exp(-z)` to exceed floating point limits (~709.78 in float64).
- **Fix:** Clip `z` into the safe range `np.clip(z, -500.0, 500.0)` or compute numerically stable sigmoid piecewise:
  `np.where(z >= 0, 1.0 / (1.0 + np.exp(-z)), np.exp(z) / (1.0 + np.exp(z)))`.

### 2. Log of Zero in Binary Cross-Entropy
- **Symptom:** `RuntimeWarning: divide by zero encountered in log` returning `NaN` loss.
- **Cause:** Predicted probability `p` reaches exactly `0.0` or `1.0`.
- **Fix:** Clip probabilities `np.clip(p, 1e-15, 1.0 - 1e-15)`.

### 3. Exploding Gradients without Feature Scaling
- **Symptom:** Loss increases to infinity or oscillates wildly.
- **Cause:** Features with unscaled large magnitudes produce massive gradient steps.
- **Fix:** Standardize features using `StandardScaler` (zero mean, unit variance) before gradient descent.

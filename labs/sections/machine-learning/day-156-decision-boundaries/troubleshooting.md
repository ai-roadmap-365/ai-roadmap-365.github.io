# Troubleshooting Guide for Day 156

## Common Issues

### 1. Division by Zero in Boundary Slope
- **Symptom:** `ZeroDivisionError: float division by zero` when calculating `-w[0] / w[1]`.
- **Cause:** The weight `w[1]` is exactly zero, meaning the decision boundary is a vertical line `x1 = -b / w[0]`.
- **Fix:** Handle vertical lines separately by checking `abs(w[1]) < 1e-12`.

### 2. High Polynomial Degree Overfitting
- **Symptom:** Training accuracy reaches 100% but decision boundaries form wild loops and isolated islands.
- **Cause:** High degree polynomial expansions (degree >= 5) introduce excessive capacity without regularization.
- **Fix:** Apply L2 regularization (`C=1.0` or smaller) to penalize large polynomial weights.

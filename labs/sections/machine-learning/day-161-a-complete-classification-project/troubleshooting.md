# Troubleshooting Guide for Day 161

## Common Issues

### 1. Test Set Evaluated Multiple Times
- **Symptom:** `RuntimeError: Test set evaluation can only be executed ONCE to prevent leakage!`
- **Cause:** Calling `evaluate_test` repeatedly during model experimentation.
- **Fix:** Use the validation set (`X_val, y_val`) for all iterative experimentation and threshold tuning. Only call `evaluate_test` once as the final sign-off.

### 2. Feature Scale Leakage Across Splits
- **Symptom:** Test set performance fails to replicate when deployed in production.
- **Cause:** Calling `StandardScaler.fit_transform` on the combined dataset before train-test splitting.
- **Fix:** Call `fit_transform` on `X_train` only; then call `transform` (without `fit`) on `X_val` and `X_test`.

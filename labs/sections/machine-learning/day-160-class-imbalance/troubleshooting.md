# Troubleshooting Guide for Day 160

## Common Issues

### 1. Data Leakage from Resampling BEFORE Cross-Validation
- **Symptom:** Cross-validation reports 99% F1 score, but the model fails completely on new held-out test data.
- **Cause:** Applying SMOTE or oversampling to the full dataset before `train_test_split` leaks synthetic copies of test samples into the training set.
- **Fix:** ALWAYS split your data first (or use `imblearn.pipeline.Pipeline`). Resampling must be applied strictly to the training fold only.

### 2. Extreme Precision Collapse with Aggressive Undersampling
- **Symptom:** Recall reaches 95%, but Precision plummets to 2% (flooding the system with false alarms).
- **Cause:** Discarding 99% of majority samples shifts the prior distribution seen by the model.
- **Fix:** Combine moderate cost-weighting with threshold tuning rather than extreme undersampling, or apply probability calibration.

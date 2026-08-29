# Troubleshooting Guide for Day 167

## Common Issues

### 1. Data Leakage from Preprocessing Before Cross-Validation Splitting
- **Symptom:** Validation scores are artificially inflated (e.g. 98% CV score but 75% production score).
- **Cause:** Calling `scaler.fit_transform(X)` or `target_encoder.fit_transform(X, y)` on the entire dataset before running K-Fold CV leaks validation statistics into the training folds.
- **Fix:** Always wrap transformers and models inside a scikit-learn `Pipeline` or fit transformers strictly on `X_train_fold` inside the loop.

### 2. Group Leakage Across Patient or User Records
- **Symptom:** Model memorizes patient-specific biological artifacts instead of pathology.
- **Cause:** Using standard K-Fold when multiple rows belong to the same patient (e.g. 5 MRI scans per patient).
- **Fix:** Use `GroupKFold` or `StratifiedGroupKFold` on patient IDs so entire patient profiles are isolated to a single fold.

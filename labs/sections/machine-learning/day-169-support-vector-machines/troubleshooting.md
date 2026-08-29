# Troubleshooting Guide for Day 169

## Common Issues

### 1. Training SVMs Without Feature Standardization
- **Symptom:** RBF SVM produces 50% random-guess accuracy, or solver fails to converge after 100,000 iterations.
- **Cause:** SVMs compute Euclidean distances `||x - z||^2`. A feature with scale 10,000 dominates all other features.
- **Fix:** ALWAYS wrap SVMs in a `StandardScaler()` pipeline.

### 2. O(N^2) / O(N^3) Memory and Compute Blowup on Large Datasets
- **Symptom:** Kernel SVM hangs indefinitely on datasets with `N > 50,000` samples.
- **Cause:** Computing the kernel Gram matrix requires storing and factoring an `N x N` matrix (50,000 x 50,000 = 2.5 billion floats = 20 GB RAM).
- **Fix:** Use `LinearSVC` (LibLinear, $O(N)$) or SGDClassifier(loss='hinge') for large datasets, or switch to LightGBM.

# Troubleshooting Guide for Day 157

## Common Issues

### 1. Feature Scale Dominance
- **Symptom:** KNN predictions depend almost entirely on one single feature (e.g. Income in dollars) while ignoring all others (e.g. Age in years).
- **Cause:** Euclidean distance squares the raw numerical differences. A feature with scale 10,000 dominates a feature with scale 1.
- **Fix:** Always standardize all numeric features using `StandardScaler` (`(x - mu) / sigma`) before computing distance matrices.

### 2. Slow Inference on Large Datasets ($O(N \cdot d)$)
- **Symptom:** Model training is instantaneous (`fit` does nothing), but `predict` takes minutes on 100,000 samples.
- **Cause:** Brute force KNN computes distances to every single training point for every query.
- **Fix:** For low-to-moderate dimensions ($d \le 20$), use spatial indexing trees (`KDTree` or `BallTree`). For large datasets, consider approximate nearest neighbors (HNSW / FAISS).

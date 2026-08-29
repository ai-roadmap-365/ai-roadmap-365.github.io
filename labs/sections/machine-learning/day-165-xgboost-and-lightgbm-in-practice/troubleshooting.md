# Troubleshooting Guide for Day 165

## Common Issues

### 1. High Memory Usage During Split Finding on Continuous Data
- **Symptom:** Out-of-memory errors when training gradient boosting on datasets with millions of rows.
- **Cause:** Exact greedy CART splits sort every continuous feature column at every node: `O(D * N * log N)`.
- **Fix:** Use histogram-based gradient boosting (`HistGradientBoostingClassifier`, LightGBM, or XGBoost `tree_method='hist'`), which reduces memory by 8x and bin split finding to `O(D * 256)`.

### 2. Overfitting with Leaf-Wise (Best-First) Tree Growth
- **Symptom:** Deep asymmetrical tree branches memorizing small data subsets.
- **Cause:** LightGBM defaults to leaf-wise growth (`max_leaf_nodes=31`), which splits the highest-gain leaf regardless of depth.
- **Fix:** Set `max_depth` alongside `max_leaf_nodes` or increase `min_child_samples` to enforce leaf regularization.

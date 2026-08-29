# Troubleshooting Guide for Day 163

## Common Issues

### 1. Inconsistent OOB Predictions When Number of Estimators is Small
- **Symptom:** Samples with zero OOB evaluations (`oob_counts[i] == 0`) throwing division by zero.
- **Cause:** When `B` is very small (e.g. `B < 5`), some samples may be chosen in every bootstrap replicate.
- **Fix:** Filter `evaluated = oob_counts > 0` before calculating OOB score or increase `n_estimators >= 15`.

### 2. High Tree Correlation Due to Large `max_features`
- **Symptom:** Random forest performs no better than a single decision tree.
- **Cause:** Setting `max_features = D` eliminates random subspace decorrelation, causing all trees to split on the same dominant feature.
- **Fix:** Use `max_features = 'sqrt'` (i.e. `sqrt(D)`) for classification and `max_features = D // 3` for regression.

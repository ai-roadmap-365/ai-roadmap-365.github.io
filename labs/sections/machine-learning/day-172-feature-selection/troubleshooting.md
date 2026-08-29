# Troubleshooting Guide for Day 172

## Common Issues

### 1. Selection Bias / Data Leakage in Feature Selection
- **Symptom:** Cross-validation accuracy is 98%, but holdout test accuracy plunges to 65%.
- **Cause:** Selecting top 50 features on the FULL dataset before running cross-validation splits.
- **Fix:** Perform feature selection strictly INSIDE each cross-validation fold using a scikit-learn `Pipeline`.

### 2. Slow RFE on High Dimensions
- **Symptom:** RFE on 10,000 features takes 4 hours.
- **Cause:** Setting `step=1` requires fitting 10,000 successive models.
- **Fix:** Use a multi-stage funnel: first apply a fast Filter method (Variance/Mutual Information) to drop from 10,000 to 500, then run RFE with `step=10` or `step=0.1`.
